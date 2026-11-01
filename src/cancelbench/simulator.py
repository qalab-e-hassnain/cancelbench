"""Single-resource, discrete-event reference model. All durations are virtual ms.

The world knows an intent at source time; the runtime learns it after transport
delay. This distinction exposes the limit of fencing against unseen revisions.
Equal-time order: source intent, delivery, compensation, commit, notification.
The release gate commits the database when ready but holds the irreversible
notification until the end-of-turn gate.
"""

from dataclasses import asdict, dataclass
import heapq
from itertools import count, product


@dataclass(frozen=True)
class Scenario:
    id: str
    kind: str = "revise"
    change_ms: int = 450
    prepare_initial_ms: int = 500
    prepare_revised_ms: int = 100
    delivery_ms: int = 0
    notification_ms: int = 200
    compensation_ms: int = 250
    turn_end_ms: int = 1000

    def __post_init__(self):
        if self.kind not in {"stable", "noop", "revise", "cancel", "chain"}:
            raise ValueError("Unknown scenario kind")
        if any(v < 0 for k, v in asdict(self).items() if k.endswith("_ms")):
            raise ValueError("Durations must be nonnegative")


@dataclass(frozen=True)
class Policy:
    name: str
    mode: str
    grace_ms: int = 0
    fence: bool = True

    def __post_init__(self):
        if self.mode not in {"wait", "eager", "guarded", "release", "debounce"} or self.grace_ms < 0:
            raise ValueError("Invalid policy")


POLICIES = (
    Policy("wait", "wait"),
    Policy("eager", "eager"),
    Policy("guarded_0", "guarded"),
    Policy("guarded_200", "guarded", 200),
    Policy("guarded_500", "guarded", 500),
    Policy("release_gate", "release"),
    Policy("guarded_no_fence", "guarded", fence=False),
)


def intent_events(s):
    """Oracle-parsed events. No text recognition is performed."""
    events = [(0, "set", 1, "305", s.prepare_initial_ms)]
    if s.kind == "noop":
        events.append((s.change_ms, "noop", 1, "305", 0))
    elif s.kind in {"revise", "chain"}:
        events.append((s.change_ms, "set", 2, "503", s.prepare_revised_ms))
        if s.kind == "chain":
            events.append((s.change_ms + 200, "set", 3, "701", s.prepare_initial_ms))
    elif s.kind == "cancel":
        events.append((s.change_ms, "cancel", 2, None, 0))
    return events


def simulate(s: Scenario, p: Policy):
    queue, serial, trace = [], count(), []
    state = {"world_version": 0, "world_target": None,
             "received_version": 0, "received_target": None,
             "db_version": 0, "db_target": None}

    def push(t, priority, action, payload):
        heapq.heappush(queue, (t, priority, next(serial), action, payload))

    def log(t, event, **extra):
        trace.append({"time_ms": t, "event": event, **extra, **state})

    for t, action, version, target, prep in intent_events(s):
        payload = {"action": action, "version": version, "target": target, "prep": prep}
        push(t, 0, "source", payload)
        push(t + (s.delivery_ms if t else 0), 1, "receive", payload)

    commits, notices = [], []
    preparations = compensations = blocked_commits = blocked_notices = 0
    while queue:
        t, _, _, event, x = heapq.heappop(queue)
        v, target = x["version"], x.get("target")
        if event == "source":
            if x["action"] != "noop":
                state.update(world_version=v, world_target=target)
            log(t, "source_" + x["action"], version=v, target=target)
        elif event == "receive":
            if x["action"] == "noop":
                log(t, "interruption_ignored", version=v)
                continue
            state.update(received_version=v, received_target=target)
            log(t, "received_" + x["action"], version=v, target=target)
            if state["db_target"] is not None:
                push(t + s.compensation_ms, 2, "compensate", {
                    "version": v, "old_db_version": state["db_version"]})
            if x["action"] == "cancel":
                continue
            preparations += 1
            start = max(t, s.turn_end_ms) if p.mode == "wait" else t
            ready = start + x["prep"]
            commit_at = max(ready, s.turn_end_ms + p.grace_ms) if p.mode == "guarded" else ready
            if p.mode == "debounce":
                commit_at = max(ready, t + p.grace_ms)
            log(t, "scheduled", version=v, target=target,
                preparation_start_ms=start, ready_ms=ready, commit_at_ms=commit_at)
            push(commit_at, 3, "commit", x)
        elif event == "compensate":
            # Compare-and-clear prevents a delayed undo from deleting a newer write.
            if state["db_version"] == x["old_db_version"] and state["db_target"] is not None:
                state.update(db_version=0, db_target=None)
                compensations += 1
                log(t, "compensated", version=v)
            else:
                log(t, "compensation_noop", version=v)
        elif event == "commit":
            if p.fence and v != state["received_version"]:
                blocked_commits += 1
                log(t, "commit_blocked", version=v, target=target)
                continue
            stale_known = v != state["received_version"]
            stale_world = v != state["world_version"]
            state.update(db_version=v, db_target=target)
            commits.append({"time_ms": t, "version": v, "target": target,
                            "stale_known": stale_known, "stale_world": stale_world})
            log(t, "committed", **commits[-1])
            release_at = max(t, s.turn_end_ms + p.grace_ms) if p.mode == "release" else t
            push(release_at + s.notification_ms, 4, "notify", x)
        elif event == "notify":
            if p.fence and v != state["received_version"]:
                blocked_notices += 1
                log(t, "notification_blocked", version=v, target=target)
                continue
            notices.append({"time_ms": t, "version": v, "target": target,
                            "stale_world": v != state["world_version"]})
            log(t, "notified", **notices[-1])

    final_v, expected = state["world_version"], state["world_target"]
    final_correct = state["db_target"] == expected
    changed = s.kind in {"revise", "cancel", "chain"}
    latest_source = max(t for t, a, *_ in intent_events(s) if a != "noop")
    horizon = max(s.turn_end_ms, latest_source)
    # Last time at which the DB became continuously correct through quiescence.
    settled_at = 0
    # Equal-time entries can alternate state; use the transition after the last
    # incorrect entry rather than the first equal-time entry.
    incorrect_indices = [i for i, e in enumerate(trace) if e["db_target"] != expected]
    if incorrect_indices and final_correct:
        i = incorrect_indices[-1] + 1
        settled_at = trace[i]["time_ms"]
    latency = max(0, settled_at - horizon) if final_correct else None
    row = {
        **asdict(s), "policy": p.name, "grace_ms": p.grace_ms,
        "final_correct": final_correct,
        "stale_known_commit": any(c["stale_known"] for c in commits),
        "stale_world_commit": any(c["stale_world"] for c in commits),
        # Retrospective: an earlier legitimate effect can later be superseded.
        "superseded_commit": changed and any(c["version"] != final_v for c in commits),
        "superseded_notification": changed and any(n["version"] != final_v for n in notices),
        "stale_world_notification": any(n["stale_world"] for n in notices),
        "preparations": preparations, "compensations": compensations,
        "blocked_commits": blocked_commits, "blocked_notifications": blocked_notices,
        "settlement_latency_ms": latency,
        "cancel_prevented": s.kind == "cancel" and not commits,
        "cancel_final_correct": s.kind == "cancel" and final_correct,
        "cancel_notice_prevented": s.kind == "cancel" and not notices,
    }
    return row, trace


def scenarios():
    index = 0
    for kind in ("stable", "noop", "revise", "cancel", "chain"):
        times = (0,) if kind == "stable" else (150, 450, 850, 1050, 1350, 1800)
        for p0 in (100, 500, 1200):
            revised_preps = (100, 500, 1200) if kind in {"revise", "chain"} else (p0,)
            for t, p1, delay, notice, compensation in product(
                times, revised_preps, (0, 100, 350), (0, 200), (0, 250)
            ):
                index += 1
                yield Scenario(f"s{index:05d}", kind, t, p0, p1, delay, notice, compensation)

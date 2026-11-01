"""Paired, per-scenario checks of the release-monotonicity results (Section 4)."""

from dataclasses import replace

from .simulator import Policy, simulate

# (earlier, later): the later policy never attempts a commit or a notification
# earlier than the earlier policy, operation by operation.
ORDERED_PAIRS = (
    ("eager", "guarded_0"), ("guarded_0", "guarded_200"), ("guarded_200", "guarded_500"),
    ("guarded_0", "wait"), ("eager", "release_gate"),
)
# Release times of these two are not ordered operation by operation.
UNORDERED_PAIRS = (("guarded_500", "wait"),)
# Endpoint decisions earlier and later than the nominal 1000 ms boundary.
ENDPOINTS_MS = (600, 800, 1000, 1200, 1400)
CHANGED = {"revise", "cancel", "chain"}


def effects(trace):
    """Versions committed, versions notified and the final source version."""
    commits = frozenset(e["version"] for e in trace if e["event"] == "committed")
    notices = frozenset(e["version"] for e in trace if e["event"] == "notified")
    final = [e for e in trace if e["event"] in {"source_set", "source_cancel"}][-1]["version"]
    return commits, notices, final


def compare(earlier, later):
    (ca, na, fa), (cb, nb, fb) = earlier, later
    sa, sb = na - {fa}, nb - {fb}
    return {"notice_violation": not nb <= na, "commit_violation": not cb <= ca,
            "fewer_superseded": sb < sa, "more_superseded": sa < sb}


def tally(results):
    keys = ("notice_violation", "commit_violation", "fewer_superseded", "more_superseded")
    return {"scenarios": len(results), **{k: sum(r[k] for r in results) for k in keys}}


def first_notice_ms(s, policy):
    """Closed-form attempt time of the initial operation's notification."""
    p0, e, n = s.prepare_initial_ms, s.turn_end_ms, s.notification_ms
    return {"eager": p0, "wait": e + p0, "release": max(p0, e),
            "guarded": max(p0, e + policy.grace_ms)}[policy.mode] + n


def analyse(cases, policies, eff, rows):
    """eff and rows are keyed by (scenario id, policy name)."""
    out = {"ordered_pairs": [], "unordered_pairs": [], "endpoint_sweep": []}
    for a, b in ORDERED_PAIRS:
        results = [compare(eff[s.id, a], eff[s.id, b]) for s in cases]
        world = sum(rows[s.id, b]["stale_world_commit"] and not rows[s.id, a]["stale_world_commit"]
                    for s in cases)
        prevention = sum(rows[s.id, a]["cancel_prevented"] and not rows[s.id, b]["cancel_prevented"]
                         for s in cases)
        out["ordered_pairs"].append({"earlier": a, "later": b, **tally(results),
                                     "world_stale_worse": world, "prevention_worse": prevention})
    for a, b in UNORDERED_PAIRS:
        out["unordered_pairs"].append({"first": a, "second": b,
                                       **tally([compare(eff[s.id, a], eff[s.id, b]) for s in cases])})
    out["release_gate_equals_guarded_0_notices"] = sum(
        eff[s.id, "release_gate"][1] == eff[s.id, "guarded_0"][1] for s in cases)

    # Any endpoint decision: eager, then gates at successively later endpoints.
    gate = Policy("gate", "guarded")
    chain = [("eager", {s.id: eff[s.id, "eager"] for s in cases})]
    for endpoint in ENDPOINTS_MS:
        chain.append((f"gate@{endpoint}", {s.id: effects(simulate(replace(s, turn_end_ms=endpoint), gate)[1])
                                           for s in cases}))
    for (a, ea), (b, eb) in zip(chain, chain[1:]):
        out["endpoint_sweep"].append({"earlier": a, "later": b,
                                      **tally([compare(ea[s.id], eb[s.id]) for s in cases])})

    # Single-change scenarios: superseded notification iff it precedes the receipt.
    checked = matched = 0
    for s in cases:
        if s.kind not in {"revise", "cancel"}:
            continue
        for p in policies:
            if not p.fence:
                continue
            predicted = first_notice_ms(s, p) < s.change_ms + s.delivery_ms
            checked += 1
            matched += predicted == rows[s.id, p.name]["superseded_notification"]
    out["closed_form"] = {"checked": checked, "matched": matched}

    # Corrections during the original turn versus after it.
    strata = {}
    for p in policies:
        for label, inside in (("within_turn", True), ("after_turn", False)):
            group = [rows[s.id, p.name] for s in cases
                     if s.kind in CHANGED and (s.change_ms < s.turn_end_ms) == inside]
            strata.setdefault(p.name, {})[label] = {
                "runs": len(group),
                "superseded_notification_rate": sum(r["superseded_notification"] for r in group) / len(group)}
    out["strata"] = strata
    return out

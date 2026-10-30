"""Probe pinned upstream tool functions with controlled in-memory dependencies."""

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import hashlib
import json
from pathlib import Path
import subprocess
from threading import Event
from typing import Any, Dict


PINS = {
    "speculative_action": "dc938b9ef7474caf07fe4ad16549c1fa8c7d268c",
    "riley": "f54b220e21cd55d812e7a4386ea865d4791b6b98",
}


def extract(path, function, class_name=None):
    tree = ast.parse(path.read_text())
    nodes = tree.body
    if class_name:
        nodes = next(node for node in nodes if isinstance(node, ast.ClassDef)
                     and node.name == class_name).body
    selected = next(node for node in nodes if isinstance(node, ast.FunctionDef)
                    and node.name == function)
    selected.decorator_list = []
    module = ast.Module(body=[selected], type_ignores=[])
    namespace = {"json": json, "Dict": Dict, "Any": Any,
                 "BCSAPI": object, "CardStatus": Status}
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    return namespace[function]


class Status(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CANCELLED = "cancelled"


class ControlledAPI:
    def __init__(self):
        self.status = "active"

    def update_card_status(self, card_id, new_status):
        self.status = new_status.value
        return self

    def model_dump(self):
        return {"status": self.status}


def race(operation, guarded):
    entered, resume = Event(), Event()
    latest_version = [1]

    def worker():
        entered.set()
        if not resume.wait(5):
            raise RuntimeError("Probe barrier timed out")
        if guarded and latest_version[0] != 1:
            return "blocked_by_local_wrapper"
        return operation()

    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(worker)
        try:
            if not entered.wait(5):
                raise RuntimeError("Worker did not reach barrier")
            latest_version[0] = 2
        finally:
            resume.set()
        result = pending.result(timeout=5)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--speculative-root", type=Path, required=True)
    parser.add_argument("--riley-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("experiments/contracts/probes.json"))
    args = parser.parse_args()
    roots = {"speculative_action": args.speculative_root, "riley": args.riley_root}
    files = {
        "speculative_action": args.speculative_root / "e-commerce/tau-bench/tau_bench/envs/retail/tools/cancel_pending_order.py",
        "riley": args.riley_root / "openai-realtime-mini/app/tools.py",
    }
    provenance = {}
    for name, root in roots.items():
        commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        if commit != PINS[name]:
            raise ValueError(f"Unexpected upstream commit for {name}: {commit}")
        relative = str(files[name].relative_to(root))
        committed = subprocess.check_output(["git", "-C", str(root), "show", f"HEAD:{relative}"])
        if files[name].read_bytes() != committed:
            raise ValueError(f"Modified upstream file: {relative}")
        provenance[name] = {"commit": commit, "path": relative,
                            "sha256": hashlib.sha256(committed).hexdigest()}
    invoke = extract(files["speculative_action"], "invoke", "CancelPendingOrder")
    dispatch = extract(files["riley"], "dispatch")
    results = []
    for guarded in (False, True):
        data = {"orders": {"order": {"status": "pending", "payment_history": [], "user_id": "user"}}}
        race(lambda: invoke(data, "order", "no longer needed"), guarded)
        results.append({"implementation": "speculative_action", "local_wrapper": guarded,
                        "effect_after_retraction": data["orders"]["order"]["status"] == "cancelled"})
        api = ControlledAPI()
        race(lambda: dispatch(api, "change_card_status", {"card_id": "card", "new_status": "frozen"}), guarded)
        results.append({"implementation": "riley", "local_wrapper": guarded,
                        "effect_after_retraction": api.status == "frozen"})
    if any(row["effect_after_retraction"] == row["local_wrapper"] for row in results):
        raise RuntimeError("Unexpected probe outcome")
    artifact = {
        "scope": "Extracted upstream functions with controlled dependencies; not full-agent or remote-database reproduction.",
        "contract": "Retraction before tool entry is a local proposed contract, not an upstream promised guarantee.",
        "wrapper_limit": "Local wrapper only; does not protect a correction arriving after its check or a remote dispatch boundary.",
        "provenance": provenance, "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()

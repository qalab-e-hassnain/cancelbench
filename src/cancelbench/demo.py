"""Print a worked late-completion race, with or without fencing."""

import argparse
import json
from .simulator import POLICIES, Scenario, simulate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", choices=[p.name for p in POLICIES], default="guarded_0")
    args = parser.parse_args()
    row, trace = simulate(Scenario("worked-example", change_ms=150,
                                   prepare_initial_ms=1200, prepare_revised_ms=100,
                                   delivery_ms=0), next(p for p in POLICIES if p.name == args.policy))
    print(json.dumps({"outcome": row, "events": trace}, indent=2))


if __name__ == "__main__":
    main()

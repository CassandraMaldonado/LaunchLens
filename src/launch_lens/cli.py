# Command-line interface to reproduce the analysis.

import argparse
import json

from .analysis import analyze_experiment
from .simulation import simulate_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an AI product experiment")
    parser.add_argument("command", choices=["analyze"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--users", type=int, default=12_000)
    args = parser.parse_args()
    print(json.dumps(analyze_experiment(simulate_experiment(args.users, args.seed)), indent=2))


if __name__ == "__main__":
    main()


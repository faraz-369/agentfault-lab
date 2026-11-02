from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentfault.experiment import run_experiment
from agentfault.models import ExperimentConfig
from agentfault.runner.engine import run_scenario
from agentfault.scenarios import load_scenarios


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentfault", description="AgentFault Lab CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one scenario")
    run.add_argument("--scenario", required=True)
    run.add_argument("--policy", default="none", choices=["none", "retry", "state_aware"])
    run.add_argument("--scenarios-dir", default="scenarios")
    run.add_argument("--output", default="results/run.json")

    bench = sub.add_parser("benchmark", help="Run scenarios across policies")
    bench.add_argument("--scenarios", nargs="+", required=True)
    bench.add_argument("--policies", nargs="+", default=["none", "retry", "state_aware"])
    bench.add_argument("--trials", type=int, default=1)
    bench.add_argument("--scenarios-dir", default="scenarios")
    bench.add_argument("--output-dir", default="results")
    bench.add_argument("--experiment-id", default="local-benchmark")

    listing = sub.add_parser("list", help="List available scenarios")
    listing.add_argument("--scenarios-dir", default="scenarios")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    scenarios = load_scenarios(args.scenarios_dir)

    if args.command == "list":
        for scenario_id, scenario in scenarios.items():
            print(f"{scenario_id}: {scenario.name}")
        return

    if args.command == "run":
        if args.scenario not in scenarios:
            raise SystemExit(f"Unknown scenario: {args.scenario}")
        result = run_scenario(scenarios[args.scenario], args.policy)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        print(json.dumps({
            "run_id": result.run_id,
            "scenario_id": result.scenario_id,
            "policy": result.policy,
            "success": result.success,
            "error": result.error,
            "tool_calls": result.tool_calls,
            "retries": result.retries,
            "invariant_violations": result.invariant_violations,
            "output": str(output),
        }, indent=2))
        return

    if args.command == "benchmark":
        config = ExperimentConfig(
            experiment_id=args.experiment_id,
            scenario_ids=args.scenarios,
            policies=args.policies,
            trials=args.trials,
            output_dir=args.output_dir,
        )
        _, report = run_experiment(config, args.scenarios_dir, args.output_dir)
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

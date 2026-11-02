from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from agentfault.analysis.report import write_report
from agentfault.models import ExperimentConfig, RunResult
from agentfault.runner.engine import run_scenario
from agentfault.scenarios import load_scenarios


def run_experiment(
    config: ExperimentConfig,
    scenarios_dir: str | Path = "scenarios",
    output_dir: str | Path | None = None,
) -> tuple[list[RunResult], dict[str, Any]]:
    scenarios = load_scenarios(scenarios_dir)
    missing = set(config.scenario_ids) - set(scenarios)
    if missing:
        raise ValueError(f"Unknown scenario ids: {', '.join(sorted(missing))}")
    if config.trials < 1:
        raise ValueError("trials must be >= 1")
    results: list[RunResult] = []
    for scenario_id in config.scenario_ids:
        scenario = scenarios[scenario_id]
        for policy in config.policies:
            for trial in range(config.trials):
                # Current core simulator is deterministic; trial index is still recorded
                # via a seed to make future stochastic extensions explicit.
                results.append(run_scenario(scenario, policy, seed=config.seed + trial))
    exp_id = config.experiment_id or str(uuid4())
    report = write_report(results, output_dir or config.output_dir, exp_id)
    return results, report

from __future__ import annotations

import json
from pathlib import Path

from agentfault.experiment import run_experiment
from agentfault.models import ExperimentConfig

root = Path(__file__).resolve().parents[1]
config_path = root / "benchmarks" / "configs" / "default.json"
config = ExperimentConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
results, report = run_experiment(
    config,
    scenarios_dir=root / "scenarios",
    output_dir=root / config.output_dir,
)
print(json.dumps(report, indent=2))
print(f"Detailed run records: {len(results)}")

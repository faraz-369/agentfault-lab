from pathlib import Path

from agentfault.experiment import run_experiment
from agentfault.models import ExperimentConfig

ROOT = Path(__file__).resolve().parents[2]


def test_experiment_writes_summary(tmp_path):
    config = ExperimentConfig(
        experiment_id="test-experiment",
        scenario_ids=["notification_timeout"],
        policies=["none", "retry"],
        trials=2,
        output_dir=str(tmp_path),
    )
    results, report = run_experiment(config, ROOT / "scenarios", tmp_path)
    assert len(results) == 4
    assert report["runs"] == 4
    assert (tmp_path / "test-experiment_summary.json").exists()
    assert (tmp_path / "test-experiment_runs.jsonl").exists()

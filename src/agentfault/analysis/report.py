from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentfault.evaluation.metrics import summarize_runs
from agentfault.models import RunResult
from agentfault.store import SQLiteRunStore


def write_report(results: list[RunResult], output_dir: str | Path, experiment_id: str) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary = summarize_runs(results)
    SQLiteRunStore(output / "agentfault.db").save_results(experiment_id, results)
    payload = {
        "experiment_id": experiment_id,
        "methodology_note": (
            "Results describe the included scenarios and configuration only; "
            "they do not establish production-wide agent reliability."
        ),
        **summary,
    }
    (output / f"{experiment_id}_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    with (output / f"{experiment_id}_runs.jsonl").open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(result.model_dump_json(exclude={"events"}) + "\n")
    for result in results:
        result.events and _write_trace(result, output)
    return payload


def _write_trace(result: RunResult, output: Path) -> None:
    trace_path = output / "traces" / f"{result.run_id}.jsonl"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("w", encoding="utf-8") as handle:
        for event in result.events:
            handle.write(event.model_dump_json() + "\n")

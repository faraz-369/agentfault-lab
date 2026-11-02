from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from agentfault.models import RunResult


SCHEMA = '''
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    policy TEXT NOT NULL,
    success INTEGER NOT NULL,
    fault_injected INTEGER NOT NULL,
    tool_calls INTEGER NOT NULL,
    retries INTEGER NOT NULL,
    duration_ms REAL NOT NULL,
    error TEXT,
    result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    step INTEGER NOT NULL,
    name TEXT NOT NULL,
    details_json TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);
CREATE INDEX IF NOT EXISTS idx_runs_experiment ON runs(experiment_id);
CREATE INDEX IF NOT EXISTS idx_events_run_sequence ON events(run_id, sequence);
'''


class SQLiteRunStore:
    """Small local persistence layer for experiment runs and event traces."""

    def __init__(self, path: str | Path = "results/agentfault.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def save_results(self, experiment_id: str, results: list[RunResult]) -> None:
        with self._connect() as conn:
            for result in results:
                conn.execute(
                    '''INSERT OR REPLACE INTO runs
                    (run_id, experiment_id, scenario_id, policy, success, fault_injected,
                     tool_calls, retries, duration_ms, error, result_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        result.run_id, experiment_id, result.scenario_id, result.policy,
                        int(result.success), int(result.fault_injected), result.tool_calls,
                        result.retries, result.duration_ms, result.error,
                        result.model_dump_json(exclude={"events"}),
                    ),
                )
                for event in result.events:
                    conn.execute(
                        '''INSERT OR REPLACE INTO events
                        (event_id, run_id, sequence, timestamp, event_type, step, name, details_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (
                            event.event_id, event.run_id, event.sequence,
                            event.timestamp.isoformat(), event.event_type.value,
                            event.step, event.name, json.dumps(event.details, default=str),
                        ),
                    )

    def count_runs(self, experiment_id: str | None = None) -> int:
        with self._connect() as conn:
            if experiment_id is None:
                row = conn.execute("SELECT COUNT(*) FROM runs").fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) FROM runs WHERE experiment_id = ?", (experiment_id,)
                ).fetchone()
            return int(row[0])

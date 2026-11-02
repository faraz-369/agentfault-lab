from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentfault.models import ExecutionEvent, EventType


class EventRecorder:
    """Append-only recorder. Sequence numbers are assigned by the recorder."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.events: list[ExecutionEvent] = []

    def emit(
        self,
        event_type: EventType,
        *,
        step: int = 0,
        name: str = "",
        details: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        event = ExecutionEvent(
            run_id=self.run_id,
            sequence=len(self.events) + 1,
            event_type=event_type,
            step=step,
            name=name,
            details=details or {},
        )
        self.events.append(event)
        return event

    def to_jsonl(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(event.model_dump_json() + "\n")

    @staticmethod
    def read_jsonl(path: str | Path) -> list[ExecutionEvent]:
        events = []
        with Path(path).open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    events.append(ExecutionEvent.model_validate_json(line))
        return events

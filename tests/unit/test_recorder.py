from agentfault.models import EventType
from agentfault.recorder.recorder import EventRecorder


def test_recorder_assigns_monotonic_sequences_and_round_trips_jsonl(tmp_path):
    recorder = EventRecorder("run-1")
    recorder.emit(EventType.RUN_STARTED)
    recorder.emit(EventType.TOOL_CALL, step=1, name="read_file")

    path = tmp_path / "trace.jsonl"
    recorder.to_jsonl(path)
    loaded = EventRecorder.read_jsonl(path)

    assert [event.sequence for event in loaded] == [1, 2]
    assert all(event.run_id == "run-1" for event in loaded)
    assert loaded[1].name == "read_file"

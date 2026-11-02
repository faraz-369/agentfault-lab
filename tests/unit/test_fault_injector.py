from agentfault.faults.injector import FaultInjector, InjectedFault
from agentfault.models import FaultSpec


def test_timeout_injects_on_configured_call():
    injector = FaultInjector(FaultSpec(
        fault_id="f1", kind="timeout", tool_name="send_notification",
        trigger_call_number=2, message="timeout"
    ))
    injector.before_call("send_notification")
    try:
        injector.before_call("send_notification")
    except InjectedFault as exc:
        assert exc.kind == "timeout"
    else:
        raise AssertionError("Expected fault on second call")


def test_unrelated_tool_does_not_trigger_fault():
    injector = FaultInjector(FaultSpec(
        fault_id="f1", kind="exception", tool_name="send_notification"
    ))
    injector.before_call("read_file")
    assert not injector.injected

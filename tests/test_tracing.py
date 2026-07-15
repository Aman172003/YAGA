from yaga.tracing import get_trace_id, trace_scope, trace_event


def test_trace_scope_registers_and_clears_trace_id() -> None:
    assert get_trace_id() is None

    with trace_scope("trace-123") as trace_id:
        assert trace_id == "trace-123"
        assert get_trace_id() == "trace-123"
        trace_event("demo.span", stage="setup")

    assert get_trace_id() is None

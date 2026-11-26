"""Tests for Prometheus metrics and OpenTelemetry tracing (FCD-11 WP-09 / WP-10)."""

from menu_it.platform.observability.metrics import (
    generate_metrics,
    record_http_request,
    record_job_execution,
    record_redis_operation,
    record_security_event,
)
from menu_it.platform.observability.tracing import (
    configure_tracing,
    extract_trace_context,
    get_current_trace_and_span_id,
    get_tracer,
    inject_trace_context,
)


def test_metrics_recording_and_generation() -> None:
    record_http_request(method="GET", endpoint="/api/v1/health", status=200, duration_seconds=0.015)
    record_redis_operation(operation="get", status="hit")
    record_job_execution(job_type="send_email", status="completed")
    record_security_event(event_type="auth.login.failed", outcome="denied")

    metrics_bytes = generate_metrics()
    metrics_str = metrics_bytes.decode("utf-8")

    assert "http_requests_total" in metrics_str
    assert "redis_operations_total" in metrics_str
    assert "background_jobs_total" in metrics_str
    assert "security_audit_events_total" in metrics_str


def test_tracing_configuration_and_context_propagation() -> None:
    configure_tracing("menu-it-test")
    tracer = get_tracer("test-tracer")

    with tracer.start_as_current_span("parent_operation"):
        trace_id, span_id = get_current_trace_and_span_id()
        assert trace_id is not None
        assert span_id is not None
        assert len(trace_id) == 32
        assert len(span_id) == 16

        headers: dict[str, str] = {}
        inject_trace_context(headers)
        assert "traceparent" in headers

        extracted = extract_trace_context(headers)
        assert extracted is not None

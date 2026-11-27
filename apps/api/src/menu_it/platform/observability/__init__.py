"""Observability package exports (FCD-11 WP-08, WP-09, WP-10)."""

from menu_it.platform.observability.metrics import (
    MetricsManager,
    generate_metrics,
    get_metrics_manager,
    record_http_request,
    record_job_execution,
    record_redis_operation,
    record_security_event,
)
from menu_it.platform.observability.redaction import (
    mask_card_number,
    redact_authorization_header,
    redact_data,
    redact_query_params,
)
from menu_it.platform.observability.tracing import (
    configure_tracing,
    extract_trace_context,
    get_current_trace_and_span_id,
    get_tracer,
    inject_trace_context,
)

__all__ = [
    "MetricsManager",
    "configure_tracing",
    "extract_trace_context",
    "generate_metrics",
    "get_current_trace_and_span_id",
    "get_metrics_manager",
    "get_tracer",
    "inject_trace_context",
    "mask_card_number",
    "record_http_request",
    "record_job_execution",
    "record_redis_operation",
    "record_security_event",
    "redact_authorization_header",
    "redact_data",
    "redact_query_params",
]

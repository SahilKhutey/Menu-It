"""OpenTelemetry distributed tracing and context propagation (FCD-11 WP-10)."""

from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

_TRACING_INITIALIZED = False


def configure_tracing(service_name: str = "menu-it-api") -> TracerProvider:
    """Configure and initialize OpenTelemetry TracerProvider."""
    global _TRACING_INITIALIZED
    current_provider = trace.get_tracer_provider()

    # If provider already set and initialized, return it
    if _TRACING_INITIALIZED and isinstance(current_provider, TracerProvider):
        return current_provider

    resource = Resource.create(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    _TRACING_INITIALIZED = True
    return provider


def get_tracer(name: str = "menu-it") -> trace.Tracer:
    """Retrieve an OpenTelemetry tracer for instrumentation."""
    return trace.get_tracer(name)


def get_current_trace_and_span_id() -> tuple[str | None, str | None]:
    """Retrieve the current active span's trace ID and span ID as formatted hex strings."""
    span = trace.get_current_span()
    if span is None or not span.get_span_context().is_valid:
        return None, None

    ctx = span.get_span_context()
    trace_id_str = format(ctx.trace_id, "032x")
    span_id_str = format(ctx.span_id, "016x")
    return trace_id_str, span_id_str


def inject_trace_context(headers: dict[str, str]) -> dict[str, str]:
    """Inject current W3C trace context (traceparent) into outgoing HTTP headers."""
    propagator = TraceContextTextMapPropagator()
    propagator.inject(headers)
    return headers


def extract_trace_context(carrier: dict[str, Any]) -> Any:
    """Extract W3C trace context from carrier headers."""
    propagator = TraceContextTextMapPropagator()
    return propagator.extract(carrier)

"""Prometheus metrics telemetry instrumentation (FCD-11 WP-09)."""

import prometheus_client
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


class MetricsManager:
    """Manager for platform operational, security, and performance metrics."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry or prometheus_client.REGISTRY

        # 1. HTTP Request Metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests received by endpoint and status",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )
        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry,
        )

        # 2. Database Connection Pool Metrics
        self.database_connections_active = Gauge(
            "database_connections_active",
            "Number of active database connections currently checked out",
            registry=self.registry,
        )

        # 3. Redis & Cache Metrics
        self.redis_operations_total = Counter(
            "redis_operations_total",
            "Redis operations count categorized by operation and outcome",
            ["operation", "status"],
            registry=self.registry,
        )

        # 4. Background Job & Worker Metrics
        self.background_jobs_total = Counter(
            "background_jobs_total",
            "Total background jobs executed categorized by job type and status",
            ["job_type", "status"],
            registry=self.registry,
        )

        # 5. Security & Rate Limiting Metrics
        self.security_audit_events_total = Counter(
            "security_audit_events_total",
            "Total security audit events logged categorized by event type and outcome",
            ["event_type", "outcome"],
            registry=self.registry,
        )
        self.rate_limit_exceeded_total = Counter(
            "rate_limit_exceeded_total",
            "Total rate limit breaches categorized by key type",
            ["key_type"],
            registry=self.registry,
        )


_DEFAULT_METRICS_MANAGER: MetricsManager | None = None


def get_metrics_manager() -> MetricsManager:
    """Retrieve global metrics manager instance."""
    global _DEFAULT_METRICS_MANAGER
    if _DEFAULT_METRICS_MANAGER is None:
        _DEFAULT_METRICS_MANAGER = MetricsManager()
    return _DEFAULT_METRICS_MANAGER


def record_http_request(method: str, endpoint: str, status: int, duration_seconds: float) -> None:
    """Record an HTTP request count and latency."""
    mgr = get_metrics_manager()
    mgr.http_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    mgr.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
        duration_seconds
    )


def record_redis_operation(operation: str, status: str = "success") -> None:
    """Record a Redis cache or queue operation."""
    mgr = get_metrics_manager()
    mgr.redis_operations_total.labels(operation=operation, status=status).inc()


def record_job_execution(job_type: str, status: str) -> None:
    """Record a background job execution."""
    mgr = get_metrics_manager()
    mgr.background_jobs_total.labels(job_type=job_type, status=status).inc()


def record_security_event(event_type: str, outcome: str) -> None:
    """Record a security event."""
    mgr = get_metrics_manager()
    mgr.security_audit_events_total.labels(event_type=event_type, outcome=outcome).inc()


def generate_metrics() -> bytes:
    """Generate latest Prometheus metrics formatted representation."""
    mgr = get_metrics_manager()
    return generate_latest(mgr.registry)

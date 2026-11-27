"""Prometheus metrics endpoint (FCD-11 WP-09)."""

from fastapi import APIRouter, Response

from menu_it.platform.observability.metrics import generate_metrics

router = APIRouter()


@router.get(
    "/metrics",
    summary="Prometheus Telemetry Metrics",
    response_class=Response,
)
async def get_metrics() -> Response:
    """Return platform metrics formatted for Prometheus scraping."""
    return Response(
        content=generate_metrics(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )

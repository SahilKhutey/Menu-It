"""
ModularMenu — Observability & Telemetry Service (ARC-07 §17.1).
"""

import logging
from typing import Any

logger = logging.getLogger("modularmenu.telemetry")


class MonitoringService:
    @staticmethod
    def record_metric(name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Records an application operational metric."""
        tag_str = " ".join(f"{k}={v}" for k, v in (tags or {}).items())
        logger.info(f"METRIC: {name}={value} {tag_str}")

    @staticmethod
    def capture_exception(exc: Exception, context: dict[str, Any] | None = None) -> None:
        """Captures an error trace safely without sensitive credentials (ARC-07 §17.1)."""
        logger.error(f"EXCEPTION: {type(exc).__name__}: {str(exc)} Context: {context}")

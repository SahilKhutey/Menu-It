"""Application logging configuration and structured JSON formatter (FCD-09 WP-04)."""

from datetime import UTC, datetime
import json
import logging
from typing import Any

from menu_it.platform.common.redaction import redact_mapping


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for production observability."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include structured context if present
        for field in ("request_id", "correlation_id", "organization_id", "user_id"):
            val = getattr(record, field, None)
            if val is not None:
                payload[field] = str(val)

        # Include extra dictionary fields with sensitive redaction
        extra_data = getattr(record, "extra_data", None)
        if isinstance(extra_data, dict):
            payload["extra"] = redact_mapping(extra_data)

        # Include exception diagnostic if available
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


class ContextLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter injecting trusted request and tenant context into record extra."""

    def process(self, msg: Any, kwargs: Any) -> tuple[Any, Any]:
        extra = kwargs.setdefault("extra", {})
        if self.extra:
            extra.update(self.extra)
        return msg, kwargs


def get_context_logger(
    name: str,
    *,
    request_id: str | None = None,
    correlation_id: str | None = None,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> ContextLoggerAdapter:
    """Obtain a logger adapter binding request and tenant execution context."""
    logger = logging.getLogger(name)
    context: dict[str, Any] = {}
    if request_id:
        context["request_id"] = str(request_id)
    if correlation_id:
        context["correlation_id"] = str(correlation_id)
    if organization_id:
        context["organization_id"] = str(organization_id)
    if user_id:
        context["user_id"] = str(user_id)
    return ContextLoggerAdapter(logger, context)


def configure_logging(level: str = "INFO", format_type: str = "text") -> None:
    """Configure consistent application logging."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(log_level)

    # Reconfigure handlers safely
    handler = logging.StreamHandler()
    if format_type.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )

    root.handlers = [handler]

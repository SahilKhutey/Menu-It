"""Health endpoint response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    application: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    ready: bool

# 21. API Observability and Telemetry

## 1. Correlation & Structured Logs
Every request receives an `X-Request-ID` attached to the request lifecycle and emitted in structured JSON application logs.
Health check endpoint `/health` reports operational status and dependency connectivity.

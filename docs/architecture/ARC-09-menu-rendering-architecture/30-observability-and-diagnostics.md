# ARC-09 §30 — Observability & Diagnostics

## 1. Metrics & Telemetry
1. **Cache Hit Ratio**: Monitored via CDN HTTP 304 response percentages (target: >85% during peak hours).
2. **Rendering Execution Duration**: Monitored in milliseconds (target: p95 < 25ms, p99 < 50ms).
3. **Core Web Vitals**:
   - LCP (Largest Contentful Paint): < 1.2s.
   - FID / INP (Interaction to Next Paint): < 100ms.
   - CLS (Cumulative Layout Shift): < 0.05.

## 2. Structured Diagnostic Logs
Failed rendering validations and conditional cache evaluations log structured JSON events:
```json
{
  "timestamp": "2026-11-22T09:40:00Z",
  "level": "INFO",
  "event": "PUBLIC_MENU_RENDERED",
  "restaurant_slug": "bhojnam-express",
  "menu_slug": "dinner-tasting",
  "version_number": 1,
  "checksum": "184736ccc2ac86fd9803e1ecdb4db9a9019d2a1d70c668d4b60cd36d298e92b1",
  "render_duration_ms": 3.8
}
```

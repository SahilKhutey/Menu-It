# FCD-11 · Document 19: Graceful Degradation, Circuit Breakers & Backpressure

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Circuit Breaker State Machine

The `CircuitBreaker` class in `menu_it.platform.reliability.circuit_breaker` protects the system from cascading failures:

```
          ┌────────────────────────────────────────┐
          │                                        │
          ▼                                        │
     ┌──────────┐   5 consecutive failures   ┌──────────┐
     │  CLOSED  ├───────────────────────────►│   OPEN   │
     └────▲─────┘                            └────┬─────┘
          │                                       │
          │ 2 consecutive                         │ Recovery timeout (30s)
          │ successes                             │ elapsed
          │                                       ▼
          │                                 ┌───────────┐
          └─────────────────────────────────┤ HALF_OPEN │
               Probe failure returns to OPEN└───────────┘
```

### State Behavior
- **CLOSED:** Normal operation. Calls pass through. Failures increment failure counter.
- **OPEN:** Fast-fail state. Calls are rejected immediately with `CircuitBreakerOpenException` without invoking the downstream dependency.
- **HALF_OPEN:** Probe state after `recovery_timeout`. Limited test calls are allowed through. If successful (`success_threshold` reached), the circuit closes; if any probe fails, it immediately re-opens.

---

## 2. Graceful Degradation Strategies

- **Cache Outage:** When Redis is down, reads query the primary database directly, and rate limits fall back to in-memory sliding windows.
- **Non-Critical Services:** If recommendation or analytics services are unavailable, the core menu browsing and ordering endpoints continue functioning normally.

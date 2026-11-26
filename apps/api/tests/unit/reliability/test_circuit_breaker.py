"""Tests for circuit breaker fault tolerance state machine (FCD-11 WP-11)."""

import asyncio

import pytest

from menu_it.platform.reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException,
    CircuitState,
)


@pytest.mark.asyncio
async def test_circuit_breaker_closed_on_success() -> None:
    cb = CircuitBreaker("payment_service", failure_threshold=3, recovery_timeout=0.1)
    assert cb.state == CircuitState.CLOSED

    async def successful_call() -> str:
        return "ok"

    result = await cb.call(successful_call)
    assert result == "ok"
    assert cb.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_circuit_breaker_trips_to_open() -> None:
    cb = CircuitBreaker("external_api", failure_threshold=2, recovery_timeout=0.1)

    async def failing_call() -> None:
        raise ValueError("Service down")

    # 1st failure
    with pytest.raises(ValueError):
        await cb.call(failing_call)
    assert cb.state == CircuitState.CLOSED

    # 2nd failure trips circuit to OPEN
    with pytest.raises(ValueError):
        await cb.call(failing_call)
    assert cb.state == CircuitState.OPEN

    # Subsequent call immediately rejected with CircuitBreakerOpenException without invoking call
    with pytest.raises(CircuitBreakerOpenException) as exc:
        await cb.call(failing_call)
    assert exc.value.name == "external_api"


@pytest.mark.asyncio
async def test_circuit_breaker_recovery_to_half_open_and_closed() -> None:
    cb = CircuitBreaker(
        "notification_service", failure_threshold=1, recovery_timeout=0.05, success_threshold=2
    )

    async def failing_call() -> None:
        raise RuntimeError("Transient timeout")

    with pytest.raises(RuntimeError):
        await cb.call(failing_call)
    assert cb.state == CircuitState.OPEN

    # Sleep past recovery timeout
    await asyncio.sleep(0.06)

    # Probe 1 in HALF_OPEN
    async def ok_call() -> str:
        return "success"

    res1 = await cb.call(ok_call)
    assert res1 == "success"
    assert cb.state == CircuitState.HALF_OPEN

    # Probe 2 reaches success_threshold=2, transitions to CLOSED
    res2 = await cb.call(ok_call)
    assert res2 == "success"
    assert cb.state == CircuitState.CLOSED

"""Unit tests for FCD-15 domain value objects, schedule engine, and configuration resolver."""

from datetime import UTC, date, datetime, time
from uuid import uuid4

import pytest

from menu_it.domain.base.errors import BusinessRuleViolationError, ValidationDomainError
from menu_it.domain.restaurant_configuration import (
    BranchConfigurationEntity,
    ExceptionType,
    HexColor,
    OpeningInterval,
    OperationalSettings,
    ScheduleExceptionEntry,
    ServiceModeConfig,
    ServiceType,
    build_effective_configuration,
    evaluate_open_status,
    resolve_service_modes,
    validate_daily_intervals,
)


def test_hex_color_validation_and_normalization() -> None:
    assert HexColor("#ff5733").normalized() == "#FF5733"
    with pytest.raises(ValidationDomainError):
        HexColor("red")
    with pytest.raises(ValidationDomainError):
        HexColor("#12345")


def test_opening_intervals_and_overlap_detection() -> None:
    morning = OpeningInterval(time(9, 0), time(14, 0))
    evening = OpeningInterval(time(17, 0), time(23, 0))
    assert validate_daily_intervals([evening, morning]) == (morning, evening)

    with pytest.raises(ValidationDomainError):
        OpeningInterval(time(10, 0), time(10, 0))

    with pytest.raises(ValidationDomainError):
        OpeningInterval(time(22, 0), time(2, 0), closes_next_day=False)

    overnight = OpeningInterval(time(22, 0), time(2, 0), closes_next_day=True)
    assert overnight.closes_next_day is True

    with pytest.raises(BusinessRuleViolationError):
        validate_daily_intervals(
            [
                OpeningInterval(time(9, 0), time(14, 0)),
                OpeningInterval(time(13, 0), time(17, 0)),
            ]
        )


def test_open_now_evaluation_with_timezone_overnight_and_exceptions() -> None:
    # Monday (0): 20:00 -> 02:00 next day in Asia/Kolkata (+05:30)
    weekly = {
        0: (OpeningInterval(time(20, 0), time(2, 0), closes_next_day=True),),
        1: (OpeningInterval(time(11, 0), time(22, 0)),),
    }
    # Tuesday 01:00 IST == Monday 19:30 UTC -> still open from Monday overnight shift!
    tue_early_ist_in_utc = datetime(2026, 11, 23, 19, 30, tzinfo=UTC)
    res = evaluate_open_status(
        now_utc=tue_early_ist_in_utc,
        timezone_name="Asia/Kolkata",
        weekly_hours=weekly,
    )
    assert res.is_open is True
    assert res.timezone == "Asia/Kolkata"

    # Holiday closure on Tuesday 2026-11-24 overrides weekly schedule
    holiday = ScheduleExceptionEntry(
        exception_date=date(2026, 11, 24),
        exception_type=ExceptionType.CLOSED,
        reason="Festival Holiday",
    )
    tue_noon_ist_in_utc = datetime(2026, 11, 24, 6, 30, tzinfo=UTC)
    closed_res = evaluate_open_status(
        now_utc=tue_noon_ist_in_utc,
        timezone_name="Asia/Kolkata",
        weekly_hours=weekly,
        exceptions=[holiday],
    )
    assert closed_res.is_open is False
    assert closed_res.source == "exception_closed"


def test_branch_explicit_false_disables_inherited_delivery() -> None:
    restaurant_services = {
        "DINE_IN": ServiceModeConfig(ServiceType.DINE_IN, enabled=True),
        "DELIVERY": ServiceModeConfig(ServiceType.DELIVERY, enabled=True),
    }
    branch_overrides = {
        "DELIVERY": ServiceModeConfig(ServiceType.DELIVERY, enabled=False),
        "DINE_IN": None,
    }
    effective = resolve_service_modes(
        restaurant_services=restaurant_services,
        branch_overrides=branch_overrides,
    )
    assert effective["DINE_IN"].enabled is True
    assert effective["DELIVERY"].enabled is False


def test_effective_configuration_precedence_and_operational_validation() -> None:
    with pytest.raises(ValidationDomainError):
        OperationalSettings(preparation_buffer_minutes=-1)
    with pytest.raises(ValidationDomainError):
        OperationalSettings(max_concurrent_orders=0)

    org_id = uuid4()
    rest_id = uuid4()
    branch_id = uuid4()
    effective = build_effective_configuration(
        organization_id=org_id,
        restaurant_id=rest_id,
        restaurant_name="Spice Garden",
        restaurant_timezone="Asia/Kolkata",
        organization_currency="INR",
        restaurant_services={
            "DINE_IN": ServiceModeConfig(ServiceType.DINE_IN, enabled=True),
            "DELIVERY": ServiceModeConfig(ServiceType.DELIVERY, enabled=True),
        },
        branch_id=branch_id,
        branch_timezone="America/New_York",
        branch_config=BranchConfigurationEntity(
            organization_id=org_id,
            restaurant_id=rest_id,
            branch_id=branch_id,
            display_name_override="Spice Garden NYC",
            service_override_enabled=True,
            service_overrides={
                "DELIVERY": ServiceModeConfig(ServiceType.DELIVERY, enabled=False),
            },
        ),
    )
    assert effective.display_name == "Spice Garden NYC"
    assert effective.timezone == "America/New_York"
    assert effective.currency_code == "INR"
    assert effective.enabled_services == ("DINE_IN",)

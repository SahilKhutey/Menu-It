"""Contract tests verifying API transport schema contracts (FCD-06)."""

from datetime import UTC, datetime
from uuid import uuid4

from menu_it.contracts.common import (
    AddressDTO,
    APIResponse,
    MoneyDTO,
    ResponseMetadata,
)
from menu_it.contracts.errors import APIError, APIErrorDetail


def test_api_response_envelope_structure() -> None:
    req_id = uuid4()
    meta = ResponseMetadata(request_id=req_id, timestamp=datetime.now(UTC))
    resp = APIResponse[dict[str, str]](
        success=True,
        data={"status": "healthy"},
        error=None,
        meta=meta,
    )

    data = resp.model_dump(mode="json")
    assert data["success"] is True
    assert data["data"] == {"status": "healthy"}
    assert data["error"] is None
    assert data["meta"]["request_id"] == str(req_id)


def test_api_error_contract() -> None:
    detail = APIErrorDetail(field="email", message="Invalid email", code="INVALID_FORMAT")
    error = APIError(
        code="VALIDATION_FAILED",
        message="Request payload failed validation",
        details=[detail.model_dump()],
    )
    dumped = error.model_dump()
    assert dumped["code"] == "VALIDATION_FAILED"
    assert len(dumped["details"]) == 1
    assert dumped["details"][0]["field"] == "email"


def test_value_transfer_objects() -> None:
    money = MoneyDTO(amount="49.99", currency="USD")
    assert money.amount == "49.99"
    assert money.currency == "USD"

    address = AddressDTO(
        line_1="100 Innovation Way",
        locality="Austin",
        country_code="US",
        postal_code="78701",
    )
    assert address.line_1 == "100 Innovation Way"
    assert address.country_code == "US"
    assert address.line_2 is None

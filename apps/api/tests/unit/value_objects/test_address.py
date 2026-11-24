"""Unit tests for Address value object (FCD-06 §7.7, §18.4)."""

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.address import Address


def test_address_valid_and_normalization() -> None:
    addr = Address(
        line_1="  12 Main Road  ",
        line_2="  Suite 4B  ",
        locality="  Bilaspur  ",
        administrative_area="  Chhattisgarh  ",
        postal_code="  495001  ",
        country_code="in",
    )
    assert addr.line_1 == "12 Main Road"
    assert addr.line_2 == "Suite 4B"
    assert addr.locality == "Bilaspur"
    assert addr.administrative_area == "Chhattisgarh"
    assert addr.postal_code == "495001"
    assert addr.country_code == "IN"


def test_address_requires_line_1_locality_and_country() -> None:
    with pytest.raises(ValidationDomainError):
        Address(line_1="", locality="Bilaspur", country_code="IN")

    with pytest.raises(ValidationDomainError):
        Address(line_1="12 Main Rd", locality="", country_code="IN")

    with pytest.raises(ValidationDomainError):
        Address(line_1="12 Main Rd", locality="Bilaspur", country_code="IND")  # Must be 2 chars

    with pytest.raises(ValidationDomainError):
        Address(line_1="12 Main Rd", locality="Bilaspur", country_code="12")

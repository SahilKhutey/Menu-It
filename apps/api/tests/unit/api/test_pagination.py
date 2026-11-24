"""Unit tests for pagination parameters and metadata calculation (FCD-07 WP-07)."""

import pytest
from pydantic import ValidationError

from menu_it.api.schemas.pagination import PaginationMeta, PaginationParams


def test_pagination_params_defaults():
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == 20
    assert params.offset == 0


def test_pagination_params_custom():
    params = PaginationParams(page=3, page_size=50)
    assert params.page == 3
    assert params.page_size == 50
    assert params.offset == 100


def test_pagination_params_validation_failure():
    with pytest.raises(ValidationError):
        PaginationParams(page=0)

    with pytest.raises(ValidationError):
        PaginationParams(page_size=0)

    with pytest.raises(ValidationError):
        PaginationParams(page_size=101)


def test_pagination_meta_calculation_single_page():
    meta = PaginationMeta.build(page=1, page_size=20, total_items=15)
    assert meta.page == 1
    assert meta.page_size == 20
    assert meta.total_items == 15
    assert meta.total_pages == 1
    assert not meta.has_next
    assert not meta.has_previous


def test_pagination_meta_calculation_multiple_pages():
    meta = PaginationMeta.build(page=2, page_size=10, total_items=25)
    assert meta.page == 2
    assert meta.page_size == 10
    assert meta.total_items == 25
    assert meta.total_pages == 3
    assert meta.has_next
    assert meta.has_previous


def test_pagination_meta_calculation_zero_items():
    meta = PaginationMeta.build(page=1, page_size=20, total_items=0)
    assert meta.total_items == 0
    assert meta.total_pages == 0
    assert not meta.has_next
    assert not meta.has_previous

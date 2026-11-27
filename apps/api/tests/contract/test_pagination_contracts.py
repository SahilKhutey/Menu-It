"""Contract tests verifying pagination schema contracts (FCD-06)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from menu_it.contracts.common import ResponseMetadata
from menu_it.contracts.pagination import (
    PaginatedResponse,
    PaginationQuery,
    build_pagination_meta,
)


def test_pagination_query_validation() -> None:
    query = PaginationQuery(page=2, page_size=50)
    assert query.page == 2
    assert query.page_size == 50

    with pytest.raises(ValidationError):
        PaginationQuery(page=0)  # ge=1

    with pytest.raises(ValidationError):
        PaginationQuery(page_size=150)  # le=100


def test_build_pagination_meta() -> None:
    meta = build_pagination_meta(total_items=95, page=1, page_size=20)
    assert meta.total_pages == 5
    assert meta.has_next is True
    assert meta.has_previous is False

    meta_last = build_pagination_meta(total_items=95, page=5, page_size=20)
    assert meta_last.total_pages == 5
    assert meta_last.has_next is False
    assert meta_last.has_previous is True

    meta_empty = build_pagination_meta(total_items=0, page=1, page_size=20)
    assert meta_empty.total_pages == 0
    assert meta_empty.has_next is False
    assert meta_empty.has_previous is False


def test_paginated_response_serialization() -> None:
    meta = build_pagination_meta(total_items=2, page=1, page_size=20)
    req_meta = ResponseMetadata(request_id=uuid4(), timestamp=datetime.now(UTC))
    resp = PaginatedResponse[str](
        data=["item-1", "item-2"],
        pagination=meta,
        meta=req_meta,
    )
    dumped = resp.model_dump(mode="json")
    assert len(dumped["data"]) == 2
    assert dumped["pagination"]["total_items"] == 2

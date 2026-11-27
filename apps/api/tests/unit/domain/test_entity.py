"""Unit tests for Entity domain primitives (FCD-06 §6.2, §18.2)."""

from uuid import uuid4

from menu_it.domain.base.entity import Entity


class SampleEntity(Entity):
    name: str = ""


def test_entities_with_same_type_and_id_are_equal() -> None:
    entity_id = uuid4()
    first = SampleEntity(id=entity_id)
    second = SampleEntity(id=entity_id)
    first.name = "Alice"
    second.name = "Bob"

    assert first == second
    assert hash(first) == hash(second)


def test_entities_with_different_ids_are_not_equal() -> None:
    first = SampleEntity(id=uuid4())
    second = SampleEntity(id=uuid4())

    assert first != second
    assert hash(first) != hash(second)


def test_entity_not_equal_to_non_entity() -> None:
    entity = SampleEntity(id=uuid4())
    assert entity != "string-id"
    assert entity != 123

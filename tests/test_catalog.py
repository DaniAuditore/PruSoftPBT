from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given
from hypothesis import strategies as st

from catalog import Catalog
from tests.strategies import BOOK_LISTS, FIELDS, INVALID_FIELDS, INVALID_IDS


def populated(fields):
    catalog = Catalog()
    for title, pages in fields:
        catalog.create(title, pages)
    return catalog


@given(BOOK_LISTS)
def test_create_adds_one_unique_normalized_record(fields):
    catalog = Catalog()
    for expected_id, (title, pages) in enumerate(fields, start=1):
        before = catalog.list_books()
        book = catalog.create(title, pages)
        assert (book.id, book.title, book.pages) == (expected_id, title.strip(), pages)
        assert catalog.list_books() == before + (book,)
        assert catalog.read(book.id) == book
    assert len({book.id for book in catalog.list_books()}) == len(fields)


@given(BOOK_LISTS, FIELDS, st.data())
def test_read_is_pure_and_snapshots_are_immutable(fields, replacement, data):
    catalog = populated(fields)
    snapshot = catalog.list_books()
    target = data.draw(st.sampled_from(snapshot))
    assert catalog.read(target.id) == target
    assert catalog.list_books() == snapshot
    with pytest.raises(FrozenInstanceError):
        target.title = "External mutation"
    with pytest.raises(TypeError):
        snapshot[0] = target
    assert catalog.read(target.id) == target
    catalog.update(target.id, *replacement)
    assert snapshot[target.id - 1] == target
    assert target.title == fields[target.id - 1][0].strip()


@given(BOOK_LISTS, FIELDS, st.data())
def test_update_preserves_identity_cardinality_and_other_records(fields, new, data):
    catalog = populated(fields)
    before = catalog.list_books()
    target = data.draw(st.sampled_from(before))
    updated = catalog.update(target.id, *new)
    assert (updated.id, updated.title, updated.pages) == (
        target.id,
        new[0].strip(),
        new[1],
    )
    assert catalog.read(target.id) == updated
    assert len(catalog.list_books()) == len(before)
    assert catalog.list_books() == tuple(
        updated if book.id == target.id else book for book in before
    )


@given(BOOK_LISTS, FIELDS, st.data())
def test_delete_removes_only_target_and_never_reuses_id(fields, new, data):
    catalog = populated(fields)
    before = catalog.list_books()
    target = data.draw(st.sampled_from(before))
    assert catalog.delete(target.id) == target
    assert catalog.list_books() == tuple(book for book in before if book != target)
    with pytest.raises(KeyError):
        catalog.read(target.id)
    assert catalog.create(*new).id == len(fields) + 1


@given(BOOK_LISTS, INVALID_FIELDS, st.data())
def test_invalid_fields_do_not_mutate_or_consume_ids(fields, invalid, data):
    catalog = populated(fields)
    before = catalog.list_books()
    target = data.draw(st.sampled_from(before))
    with pytest.raises(ValueError):
        catalog.create(*invalid)
    assert catalog.list_books() == before
    with pytest.raises(ValueError):
        catalog.update(target.id, *invalid)
    assert catalog.list_books() == before
    assert catalog.create("Valid", 1).id == len(fields) + 1


@given(BOOK_LISTS, INVALID_IDS)
def test_invalid_ids_are_rejected_without_mutation(fields, invalid_id):
    catalog = populated(fields)
    before = catalog.list_books()
    for operation in (catalog.read, catalog.delete):
        with pytest.raises(ValueError):
            operation(invalid_id)
        assert catalog.list_books() == before
    with pytest.raises(ValueError):
        catalog.update(invalid_id, "Valid", 1)
    assert catalog.list_books() == before


@given(BOOK_LISTS, st.integers(min_value=1, max_value=1000))
def test_missing_ids_do_not_mutate(fields, offset):
    catalog = populated(fields)
    before = catalog.list_books()
    missing_id = len(fields) + offset
    for operation in (catalog.read, catalog.delete):
        with pytest.raises(KeyError):
            operation(missing_id)
        assert catalog.list_books() == before
    with pytest.raises(KeyError):
        catalog.update(missing_id, "", 0)
    assert catalog.list_books() == before

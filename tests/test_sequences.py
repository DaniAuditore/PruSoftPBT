import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from catalog import Catalog
from tests.strategies import FIELDS, INVALID_FIELDS


class CatalogSequences(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.catalog = Catalog()
        self.model = {}
        self.next_id = 1

    @rule(fields=FIELDS)
    def create(self, fields):
        book = self.catalog.create(*fields)
        assert (book.id, book.title, book.pages) == (
            self.next_id,
            fields[0].strip(),
            fields[1],
        )
        self.model[self.next_id] = (fields[0].strip(), fields[1])
        self.next_id += 1

    @rule(
        operation=st.sampled_from(["read", "update", "delete"]),
        selector=st.integers(min_value=0, max_value=1000),
        fields=FIELDS,
    )
    def access(self, operation, selector, fields):
        # Include live, deleted, and not-yet-issued IDs without preconditions.
        book_id = selector % (self.next_id + 1) + 1
        method = getattr(self.catalog, operation)
        args = (book_id, *fields) if operation == "update" else (book_id,)
        if book_id not in self.model:
            with pytest.raises(KeyError):
                method(*args)
            return
        expected = self.model[book_id]
        if operation == "update":
            expected = (fields[0].strip(), fields[1])
            self.model[book_id] = expected
        book = method(*args)
        assert (book.id, book.title, book.pages) == (book_id, *expected)
        if operation == "delete":
            del self.model[book_id]

    @rule(fields=INVALID_FIELDS)
    def invalid_write(self, fields):
        with pytest.raises(ValueError):
            self.catalog.create(*fields)
        if self.model:
            with pytest.raises(ValueError):
                self.catalog.update(min(self.model), *fields)

    @invariant()
    def entire_catalog_matches_model(self):
        books = self.catalog.list_books()
        assert [(book.id, book.title, book.pages) for book in books] == [
            (book_id, *fields) for book_id, fields in sorted(self.model.items())
        ]
        assert len({book.id for book in books}) == len(books)
        assert all(0 < book.id < self.next_id for book in books)
        assert all(
            book.title == book.title.strip()
            and 1 <= len(book.title) <= 120
            and type(book.pages) is int
            and 1 <= book.pages <= 10_000
            for book in books
        )


TestCatalogSequences = CatalogSequences.TestCase
TestCatalogSequences.settings = settings(max_examples=50, stateful_step_count=30)

"""A single-threaded, in-memory book catalog with atomic validation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Book:
    id: int
    title: str
    pages: int


def _validate_fields(title: str, pages: int) -> tuple[str, int]:
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
        raise ValueError("title must be a nonblank string of at most 120 characters")
    if type(pages) is not int or not 1 <= pages <= 10_000:
        raise ValueError("pages must be an integer between 1 and 10000")
    return title.strip(), pages


class Catalog:
    def __init__(self) -> None:
        self._books: dict[int, Book] = {}
        self._next_id = 1

    def create(self, title: str, pages: int) -> Book:
        title, pages = _validate_fields(title, pages)
        book = Book(self._next_id, title, pages)
        self._books[book.id] = book
        self._next_id += 1
        return book

    def read(self, book_id: int) -> Book:
        if type(book_id) is not int or book_id < 1:
            raise ValueError("book ID must be a positive integer")
        return self._books[book_id]

    def update(self, book_id: int, title: str, pages: int) -> Book:
        self.read(book_id)
        title, pages = _validate_fields(title, pages)
        book = Book(book_id, title, pages)
        self._books[book_id] = book
        return book

    def delete(self, book_id: int) -> Book:
        book = self.read(book_id)
        del self._books[book_id]
        return book

    def list_books(self) -> tuple[Book, ...]:
        return tuple(self._books.values())

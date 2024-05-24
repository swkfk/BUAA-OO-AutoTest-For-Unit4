from typing import Dict

from ..Model.Book import Book
from ..Exceptions.UnexpectedException import Unexpected

class BookStorage:
    def __init__(self) -> None:
        self.books: Dict[Book, int] = {}

    def __getitem__(self, key: Book) -> int:
        if key in self.books:
            return self.books[key]
        return 0

    def __contains__(self, item: Book) -> bool:
        return item in self.books

    def __iter__(self):
        return iter(self.books)

    def put(self, book: Book):
        if book in self:
            self.books[book] += 1
        else:
            self.books[book] = 1

    def get(self, book: Book):
        if book not in self or self.books[book] <= 0:
            raise Unexpected("M.B.g", "Book not in the storage when taking out")
        if self.books[book] == 1:
            del self.books[book]
        else:
            self.books[book] -= 1


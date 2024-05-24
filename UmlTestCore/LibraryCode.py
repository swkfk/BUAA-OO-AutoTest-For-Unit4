from typing import Dict

from .Model.Book import Book
from .Manager.BookStorage import BookStorage

class Library:
    def __init__(self) -> None:
        self.book_shelf = BookStorage()
        self.borrow_return_office = BookStorage()
        self.appoint_office = BookStorage()

    def init_inventory(self, inventory: Dict[Book, int]):
        self.book_shelf.books |= inventory

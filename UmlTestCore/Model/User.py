from typing import List

from .Book import Book
from ..Exceptions.BadBehaviorException import BorrowInvalidBook
from ..Exceptions.UnexpectedException import Unexpected
from ..Manager.Command import CommandInfo

class User:
    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        self.owned_book: List[Book] = []

    def on_accept_borrow(self, book: Book, command: CommandInfo):
        if book.type == Book.Type.A:
            raise BorrowInvalidBook(command, "borrow A type book")
        if book.type == Book.Type.B and any((b.type == Book.Type.B for b in self.owned_book)):
            raise BorrowInvalidBook(command, "borrow two B type books at a time")
        if any((b == book for b in self.owned_book)):
            raise BorrowInvalidBook(command, "borrow same books at a time")

        self.owned_book.append(book)

    def on_return_book(self, book: Book, command: CommandInfo):
        if book not in self.owned_book:
            raise Unexpected("M.U.orb", "Return A Non-Exist Book " + str(command))
        self.owned_book.remove(book)

    def on_accept_pick(self, book: Book, command: CommandInfo):
        self.on_accept_borrow(book, command)

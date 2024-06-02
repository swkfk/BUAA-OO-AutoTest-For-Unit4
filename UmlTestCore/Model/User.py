from typing import List
from datetime import date

from .Book import Book
from .Order import Order
from ..Exceptions.BadBehaviorException import BorrowInvalidBook, BadReturnOverdue
from ..Exceptions.UnexpectedException import Unexpected
from ..Manager.Command import CommandInfo

class User:
    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        self.owned_book: List[Book] = []
        self.appoints: List[Order] = []

    def core_dump(self) -> str:
        sb = f"{self.user_id} Owned {len(self.owned_book)} books and {len(self.appoints)} appoints\n"
        sb += "".join(f"  Book: {book}\n" for book in self.owned_book)
        sb += "".join(f"  Appo: {order.book}\n" for order in self.appoints)
        return sb

    def on_accept_borrow(self, book: Book, command: CommandInfo, now_date: date):
        self.check_borrow(book, command)
        book.mark_borrow(now_date)
        self.owned_book.append(book)

    def on_return_book(self, book: Book, command: CommandInfo, overdue: bool, now_date: date):
        if book not in self.owned_book:
            raise Unexpected("M.U.orb", "Return A Non-Exist Book " + str(command))
        b = self.owned_book[self.owned_book.index(book)]
        return_date = b.return_date
        if return_date is None:
            raise Unexpected("M.U.orb.2", "Book does not have a recorded return date " + str(now_date))
        real_overdue = return_date < now_date
        if (real_overdue, overdue) == (True, False):
            raise BadReturnOverdue(command, f"Overdue at {return_date}, now is {now_date}. Overdue!")
        if (real_overdue, overdue) == (False, True):
            raise BadReturnOverdue(command, f"Overdue at {return_date}, now is {now_date}. Not Overdue!")
        b.return_date = None
        self.owned_book.remove(book)

    def on_accept_pick(self, book: Book, command: CommandInfo, now_date: date):
        self.on_accept_borrow(book, command, now_date)
        if not self.has_ordered(book):
            raise Unexpected("M.U.oap", "Pick a book that is not wanted " + str(command))
        self.appoints.remove(Order(self.user_id, book))

    def has_ordered(self, book: Book):
        return Order(self.user_id, book) in self.appoints

    def check_borrow(self, book: Book, command: CommandInfo, addi: str = ""):
        if book.type == Book.Type.A:
            raise BorrowInvalidBook(command, "borrow A type book" + addi)
        if book.type == Book.Type.B and any((b.type == Book.Type.B for b in self.owned_book)):
            raise BorrowInvalidBook(command, "borrow two B type books at a time" + addi)
        if any((b == book for b in self.owned_book)):
            raise BorrowInvalidBook(command, "borrow same books at a time" + addi)

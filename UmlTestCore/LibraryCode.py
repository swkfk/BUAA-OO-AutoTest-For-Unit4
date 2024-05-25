from typing import Dict, List
from datetime import date

from .Model.Book import Book
from .Model import Position
from .Manager.BookStorage import BookStorage
from .Manager.Command import CommandInfo
from .Manager.Request import MoveRequest
from .Exceptions.BadBehaviorException import BookRemainedOnBro, OverdueBookRemained, BookMovementInvlid
from .Exceptions.UnexpectedException import Unexpected
from .Model.User import User


class Library:
    def __init__(self) -> None:
        self.book_shelf = BookStorage()
        self.borrow_return_office = BookStorage()
        self.appoint_office: List[Book] = []
        self.users: Dict[str, User] = {}

    def init_inventory(self, inventory: Dict[Book, int]):
        self.book_shelf.books |= inventory

    def on_open_down(self, now_date: date, command: CommandInfo):
        for _ in self.borrow_return_office:
            raise BookRemainedOnBro(command)
        for book in self.appoint_office:
            if book.reserve is None:
                raise Unexpected("L.ood", "Book not reserved for anyone in appoint office")
            if book.reserve.overdue_open(now_date):
                raise OverdueBookRemained(command)

    def on_open(self, now_date: date, moves: List[MoveRequest]):
        for move in moves:
            if move.movement[0] == move.movement[1]:
                raise BookMovementInvlid(move.command, "share the same start and end")

            if move.movement[0] == Position.BS:
                self.try_get_book(self.book_shelf, move.book, move.command, "bookshelf")
            elif move.movement[0] == Position.BRO:
                self.try_get_book(self.borrow_return_office, move.book, move.command, "borrow-return-office")
            elif move.movement[0] == Position.AO:
                for i, book in enumerate(b for b in self.appoint_office if b == move.book and book.reserve_overdue(now_date, "open")):
                    self.appoint_office.pop(i); break
                else:
                    raise BookMovementInvlid(move.command, "no books overdue in the appoint-office")

            if move.movement[1] == Position.BS:
                if move.reserve_for != "":
                    raise BookMovementInvlid(move.command, "reserve for here is invalid (for bookshelf)")
                self.book_shelf.put(move.book)
            elif move.movement[1] == Position.BRO:
                if move.reserve_for != "":
                    raise BookMovementInvlid(move.command, "reserve for here is invalid (for borrow-return-office)")
                self.borrow_return_office.put(move.book)
            elif move.movement[1] == Position.AO:
                if move.reserve_for == "":
                    raise BookMovementInvlid(move.command, "reserve for is needed (for appoint-office)")
                if move.reserve_for not in self.users:
                    raise BookMovementInvlid(move.command, f"reserve for a user who is not-exist ({move.reserve_for})")
                pass

    @staticmethod
    def try_get_book(storege: BookStorage, book: Book, command: CommandInfo, pos: str = "here"):
        if book not in storege:
            raise BookMovementInvlid(command, f"there is no this book ({pos})")
        storege.get(book)
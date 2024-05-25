from typing import Dict, List, Literal
from datetime import date, timedelta

from .Book import Book
from .Order import Order
from . import Position
from ..Manager.BookStorage import BookStorage
from ..Manager.Command import CommandInfo
from ..Manager.Request import MoveRequest, NormalRequest
from ..Manager.Reserve import ReserveInfo
from ..Exceptions.BadBehaviorException import \
    BookRemainedOnBro, OverdueBookRemained, BookMovementInvlid, BorrowInvalidBook, BookPickInvlid
from ..Exceptions.UnexpectedException import Unexpected
from .User import User


class Library:
    def __init__(self) -> None:
        self.book_shelf = BookStorage()
        self.borrow_return_office = BookStorage()
        self.appoint_office: List[Book] = []
        self.users: Dict[str, User] = {}

    def init_inventory(self, inventory: Dict[Book, int]):
        self.book_shelf.books |= inventory

    def on_reject_borrow(self, request: NormalRequest):
        if request.book not in self.book_shelf:
            raise BorrowInvalidBook(request.command, "This book is not on the shelf")
        self.book_shelf.get(request.book)
        self.borrow_return_office.put(request.book)

    def on_accept_borrow(self, request: NormalRequest):
        if request.book not in self.book_shelf:
            raise BorrowInvalidBook(request.command, "This book is not on the shelf")
        if request.user_id not in self.users:
            raise Unexpected("L.ob", f"user not exists ({request.user_id})")
        self.book_shelf.get(request.book)
        self.users[request.user_id].on_accept_borrow(request.book, request.command)

    def on_return(self, request: NormalRequest):
        if request.user_id not in self.users:
            raise Unexpected("L.or", f"user not exists ({request.user_id})")
        self.users[request.user_id].on_return_book(request.book, request.command)
        self.borrow_return_office.put(request.book)

    def on_accept_order(self, request: NormalRequest):
        if request.user_id not in self.users:
            raise Unexpected("L.oao", f"user not exists ({request.user_id})")
        self.users[request.user_id].check_borrow(request.book, request.command, " (Appointment)")
        self.users[request.user_id].appoints.append(Order(request.user_id, request.book))

    def on_accept_pick(self, request: NormalRequest, now_date: date):
        if request.user_id not in self.users:
            raise Unexpected("L.oap", f"user not exists ({request.user_id})")
        if not self.has_pickable_order(request, now_date):
            raise BookPickInvlid(request.command, "the appoint shall not be accepted")

        for i in range(len(self.appoint_office)):
            book = self.appoint_office[i]
            if book.is_reserved_for(request.user_id) and not book.reserve_overdue(now_date, "open"):
                break
        self.appoint_office.pop(i)

        self.users[request.user_id].on_accept_pick(request.book, request.command)

    def on_reject_pick(self, request: NormalRequest, now_date: date):
        if request.user_id not in self.users:
            raise Unexpected("L.orp", f"user not exists ({request.user_id})")
        if self.has_pickable_order(request, now_date):
            raise BookPickInvlid(request.command, "the appoint shall be accepted")

    def has_pickable_order(self, request: NormalRequest, now_date: date):
        user = self.users[request.user_id]
        if not Order(request.user_id, request.book) in user.appoints:
            raise Unexpected("L.hpo", "user has no such order")
        for book in self.appoint_office:
            if book.is_reserved_for(user) and not book.reserve_overdue(now_date, "open"):
                return True
        return False

    def on_open(self, now_date: date, moves: List[MoveRequest], cmd_check: CommandInfo):
        self.on_handle_move(now_date, moves, "open")

        for _ in self.borrow_return_office:
            raise BookRemainedOnBro(cmd_check)
        for book in self.appoint_office:
            if book.reserve is None:
                raise Unexpected("L.ood", "Book not reserved for anyone in appoint office")
            if book.reserve.overdue_open(now_date):
                raise OverdueBookRemained(cmd_check)

    def on_close(self, now_date: date, moves: List[MoveRequest]):
        self.on_handle_move(now_date, moves, "close")

    def on_handle_move(self, now_date: date, moves: List[MoveRequest], time: Literal["open", "close"]):
        for move in moves:
            if move.movement[0] == move.movement[1]:
                raise BookMovementInvlid(move.command, "share the same start and end")

            if move.movement[0] == Position.BS:
                self.try_get_book(self.book_shelf, move.book, move.command, "bookshelf")
            elif move.movement[0] == Position.BRO:
                self.try_get_book(self.borrow_return_office, move.book, move.command, "borrow-return-office")
            elif move.movement[0] == Position.AO:
                for i, book in enumerate(b for b in self.appoint_office if b == move.book and b.reserve_overdue(now_date, time)):
                    break
                else:
                    raise BookMovementInvlid(move.command, "no books overdue in the appoint-office")
                self.appoint_office.pop(i)
                if book.reserve is None:
                    raise Unexpected("L.ohm.1", "Book reserve info is None")
                if book.reserve.user_id not in self.users:
                    raise Unexpected("L.ohm.2", "Book reserve for a not-exist user")
                user = self.users[book.reserve.user_id]
                if Order(book.reserve.user_id, book) not in user.appoints:
                    raise Unexpected("L.ohm.3", "User has no this order")
                user.appoints.remove(Order(book.reserve.user_id, book))

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
                if not self.users[move.reserve_for].has_ordered(move.book):
                    raise BookMovementInvlid(move.command, f"user not need this book ({move.reserve_for})")
                if time == "open":
                    move.book.reserve_for(ReserveInfo(move.reserve_for, now_date))
                else:
                    move.book.reserve_for(ReserveInfo(move.reserve_for, now_date + timedelta(days=1)))
                self.appoint_office.append(move.book)

    def core_dump(self) -> str:
        sb = "Library: \n" + '-' * 20 + "\n\n"
        sb += self.book_shelf.core_dump("Bookshelf") + "\n"
        sb += self.borrow_return_office.core_dump("Borrow-Return-Office") + "\n"
        sb += "Appoint-Office: \n"
        sb += "".join([f"  {book}: {book.reserve}\n" for book in self.appoint_office])
        sb += "\nUsers: \n" + '-' * 20 + "\n"
        sb += "\n".join([f"{user.core_dump()}" for user in self.users.values()])
        sb += "\n" + '=' * 20 + "\n"
        return sb

    @staticmethod
    def try_get_book(storege: BookStorage, book: Book, command: CommandInfo, pos: str = "here"):
        if book not in storege:
            raise BookMovementInvlid(command, f"there is no this book ({pos})")
        storege.get(book)

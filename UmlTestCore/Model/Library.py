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
    BookRemainedOnBro, OverdueBookRemained, BookMovementInvlid,\
    BorrowInvalidBook, BookPickInvlid, BadReject, BadRenew, DonatedBookInvalid,\
    BookRemainedInDrift, OrderInvalidBook
from ..Exceptions.UnexpectedException import Unexpected
from .User import User


class Library:
    def __init__(self, inventory: Dict[Book, int], users: List[User]) -> None:
        self.book_shelf = BookStorage()
        self.borrow_return_office = BookStorage()
        self.appoint_office: List[Book] = []
        self.drift_corner: List[Book] = []
        self.donors: Dict[Book, str] = {}
        self.drift_count: Dict[Book, int] = {}
        self.users: Dict[str, User] = {}

        self.book_shelf.books |= inventory
        for user in users:
            self.users[user.user_id] = user

    def on_reject_borrow(self, request: NormalRequest, now_date: date):
        if not request.book.is_type_U() and request.book.type != Book.Type.A and request.book in self.book_shelf and self.book_shelf[request.book] > 0:
            self.book_shelf.get(request.book)
            self.borrow_return_office.put(request.book)
        elif request.book.is_type_U() and request.book.type != Book.Type.AU and request.book in self.drift_corner:
            self.drift_corner.remove(request.book)
            self.borrow_return_office.put(request.book)
        if request.book.is_type_U():
            if request.book in self.drift_corner:
                self.users[request.user_id].on_reject_borrow(request.book, request.command, now_date)
        else:
            if request.book in self.book_shelf and self.book_shelf[request.book] > 0:
                self.users[request.user_id].on_reject_borrow(request.book, request.command, now_date)

    def on_accept_borrow(self, request: NormalRequest, now_date: date):
        if request.book not in self.book_shelf and not request.book.is_type_U():
            raise BorrowInvalidBook(request.command, "This book is not on the shelf")
        if request.book not in self.drift_corner and request.book.is_type_U():
            raise BorrowInvalidBook(request.command, "This book is not in the drift corner")
        if request.user_id not in self.users:
            raise Unexpected("L.ob", f"user not exists ({request.user_id})")
        if request.book.is_type_U():
            self.drift_corner.remove(request.book)
        else:
            self.book_shelf.get(request.book)
        self.users[request.user_id].on_accept_borrow(request.book, request.command, now_date)

    def on_return(self, request: NormalRequest, overdue: bool, now_date: date):
        if request.user_id not in self.users:
            raise Unexpected("L.or", f"user not exists ({request.user_id})")
        self.users[request.user_id].on_return_book(request.book, request.command, overdue, now_date)
        if request.book in self.drift_count:
            self.drift_count[request.book] += 1
        self.borrow_return_office.put(request.book)

    def on_donate(self, request: NormalRequest):
        self.drift_corner.append(request.book)
        self.drift_count[request.book] = 0
        if request.user_id not in self.users:
            raise Unexpected("L.od", f"user not exists ({request.user_id})")
        self.users[request.user_id].change_credit(+2)
        self.donors[request.book] = request.user_id

    def on_accept_order(self, request: NormalRequest):
        if request.user_id not in self.users:
            raise Unexpected("L.oao", f"user not exists ({request.user_id})")
        self.users[request.user_id].check_order(request.book, request.command)
        self.users[request.user_id].appoints.append(Order(request.user_id, request.book))

    def on_reject_order(self, request: NormalRequest):
        if request.user_id not in self.users:
            raise Unexpected("L.oro", f"user not exists ({request.user_id})")
        try:
            self.users[request.user_id].check_order(request.book, request.command)
        except OrderInvalidBook:
            return
        raise BadReject(request.command, "this appointment can be accepted")

    def on_accept_renew(self, request: NormalRequest, now_date: date):
        if not self.users[request.user_id].can_renew_date(request.book, now_date):
            raise BadRenew(request.command, "cannot renew for the date")
        if not self.can_renew_book(request, request.user_id):
            raise BadRenew(request.command, "cannot renew for the books in library")
        self.users[request.user_id].on_accept_renew(request.book)

    def on_reject_renew(self, request: NormalRequest, now_date: date):
        if self.users[request.user_id].can_renew_date(request.book, now_date) and self.can_renew_book(request, request.user_id):
            raise BadRenew(request.command, "The book can be renewed.")
        self.users[request.user_id].on_reject_renew(request.book)

    def on_accept_pick(self, request: NormalRequest, now_date: date):
        if request.user_id not in self.users:
            raise Unexpected("L.oap", f"user not exists ({request.user_id})")
        if not self.has_pickable_order(request, now_date):
            raise BookPickInvlid(request.command, "the appoint shall not be accepted")

        for i in range(len(self.appoint_office)):
            book = self.appoint_office[i]
            if book == request.book and book.is_reserved_for(request.user_id) and not book.reserve_overdue(now_date, "open"):
                break
        self.appoint_office.pop(i)

        self.users[request.user_id].on_accept_pick(request.book, request.command, now_date)

    def on_reject_pick(self, request: NormalRequest, now_date: date):
        if request.user_id not in self.users:
            raise Unexpected("L.orp", f"user not exists ({request.user_id})")
        if self.has_pickable_order(request, now_date):
            user = self.users[request.user_id]
            try:
                user.check_borrow(request.book, CommandInfo('', ''))
            except:
                return
            raise BookPickInvlid(request.command, "the appoint shall be accepted")
 
    def can_renew_book(self, request: NormalRequest, user_id: str):
        if self.users[user_id].credit < 0:
            return False
        book = request.book
        if book.type == Book.Type.AU or book.type == Book.Type.BU or book.type == Book.Type.CU:
            return False
        if self.book_shelf[book] > 0:
            return True
        for user in self.users.values():
            if user.has_ordered(book):
                return False
        return True

    def has_pickable_order(self, request: NormalRequest, now_date: date):
        user = self.users[request.user_id]
        if not Order(request.user_id, request.book) in user.appoints:
            raise Unexpected("L.hpo", "user has no such order")
        for book in self.appoint_office:
            if book == request.book and book.is_reserved_for(user) and not book.reserve_overdue(now_date, "open"):
                return True
        return False

    def on_open(self, now_date: date, moves: List[MoveRequest], cmd_check: CommandInfo):
        self.on_handle_move(now_date, moves, "open")

        for _ in self.borrow_return_office:
            raise BookRemainedOnBro(cmd_check)
        for book in self.drift_corner:
            if self.drift_count.get(book, 0) >= 2:
                raise BookRemainedInDrift(cmd_check, f"book {book} has beed borrowed for {self.drift_count.get(book, 0)} times")
        for book in self.appoint_office:
            if book.reserve is None:
                raise Unexpected("L.ood", "Book not reserved for anyone in appoint office")
            if book.reserve.overdue_open(now_date):
                raise OverdueBookRemained(cmd_check)

    def on_close(self, now_date: date, moves: List[MoveRequest]):
        self.handle_overdue_close(now_date)
        self.on_handle_move(now_date, moves, "close")

    def handle_overdue_close(self, now_date: date):
        # Borrowed Overdue
        for uid, user in self.users.items():
            user.handle_overdue_close(now_date)
        for book in self.appoint_office:
            if book.reserve is None:
                raise Unexpected("L.hoc", "Book not reserved for anyone in appoint office")
            if book.reserve.overdue_precise(now_date):
                user_id = book.reserve.user_id
                user = self.users.get(user_id, None)
                if user is None:
                    raise Unexpected("L.hoc.2", "User not exists")
                user.change_credit(-3)

    def on_handle_move(self, now_date: date, moves: List[MoveRequest], time: Literal["open", "close"]):
        for move in moves:
            if move.movement[0] == move.movement[1]:
                raise BookMovementInvlid(move.command, "share the same start and end")

            if move.movement[0] is None or move.movement[1] is None:
                raise BookMovementInvlid(move.command, "unknown position")

            if move.movement[0] == Position.BS:
                self.try_get_book(self.book_shelf, move.book, move.command, "bookshelf")
            elif move.movement[0] == Position.BRO:
                self.try_get_book(self.borrow_return_office, move.book, move.command, "borrow-return-office")
            elif move.movement[0] == Position.AO:
                i = -1
                for i, book in enumerate(self.appoint_office):
                    if book == move.book and book.reserve_overdue(now_date, time):
                        break
                    else:
                        i = -1
                if i == -1:
                    raise BookMovementInvlid(move.command, "no books overdue in the appoint-office")
                else:
                    book = self.appoint_office.pop(i)
                    # print("Poped:", book)

                if book.reserve is None:
                    raise Unexpected("L.ohm.1", "Book reserve info is None")
                if book.reserve.user_id not in self.users:
                    raise Unexpected("L.ohm.2", "Book reserve for a not-exist user")
                user = self.users[book.reserve.user_id]
                if Order(book.reserve.user_id, book) not in user.appoints:
                    # print(f"Order: {book.reserve.user_id} {book}")
                    raise Unexpected("L.ohm.3", "User has no this order")
                # print(f"Removed: {book.reserve.user_id}, {book}")
                user.appoints.remove(Order(book.reserve.user_id, book))
            else:
                raise BookMovementInvlid(move.command, f"cannot move from {move.movement[0].value} when tidying")

            if move.movement[1] == Position.BS:
                if move.reserve_for != "":
                    raise BookMovementInvlid(move.command, "reserve for here is invalid (for bookshelf)")
                if move.book.is_type_U():
                    if self.drift_count.get(move.book, 0) < 2:
                        raise DonatedBookInvalid(move.command, f"this book is not qualified to goto bookshelf {self.drift_count.get(move.book, 0)} times borrowed")
                    self.book_shelf.put(Book(move.book.type.to_no_U(), move.book.id))
                    self.users[self.donors[move.book]].change_credit(+2)
                    del self.drift_count[move.book]
                    del self.donors[move.book]
                else:
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
            elif move.movement[1] == Position.BDC:
                if not move.movement[0] == Position.BRO:
                    raise BookMovementInvlid(move.command, "books moved into the drift-corner shall be from the borrow-return-office")
                if self.drift_count[move.book] >= 2:
                    raise DonatedBookInvalid(move.command, "this book is qualified to goto the bookshelf")
                self.drift_corner.append(move.book)

    def core_dump(self) -> str:
        sb = "Library: \n" + '-' * 20 + "\n\n"
        sb += self.book_shelf.core_dump("Bookshelf") + "\n"
        sb += self.borrow_return_office.core_dump("Borrow-Return-Office") + "\n"
        sb += "Drift Corner: \n"
        sb += "".join([f"  {book}: Borrowed for {self.drift_count[book]} times\n" for book in self.drift_corner])
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

from UmlTestCore.Manager.Command import CommandInfo
from UmlTestCore.Manager.Reserve import ReserveInfo
from UmlTestCore.Exceptions.BadBehaviorException import BorrowInvalidBook
from UmlTestCore.Model.Book import Book
from UmlTestCore.Model.User import User

from datetime import date

if __name__ == "__main__":
    u = User("22370000")
    try:
        u.on_accept_borrow(Book(Book.Type.A, "0001"), CommandInfo("command", "output1"))
    except BorrowInvalidBook as e:
        print(e)
    try:
        u.on_accept_borrow(Book(Book.Type.B, "0002"), CommandInfo("command", "output2"))
        u.on_accept_borrow(Book(Book.Type.B, "0003"), CommandInfo("command", "output3"))
    except BorrowInvalidBook as e:
        print(e)

    ri = ReserveInfo(u.user_id, date(2024, 5, 11))
    assert(not ri.overdue_open(date(2024, 5, 15)))
    assert(ri.overdue_open(date(2024, 5, 16)))
    assert(ri.overdue_close(date(2024, 5, 15)))

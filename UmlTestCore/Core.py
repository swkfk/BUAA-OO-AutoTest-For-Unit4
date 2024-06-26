from typing import Dict, List
from datetime import date, timedelta

from .Runner.Communicator import Reaction, Action
from .Manager.Request import MoveRequest, NormalRequest
from .Manager.Command import CommandInfo, CommandType
from .Model.Library import Library
from .Model.Book import Book
from .Model.User import User
from .Model.Order import Order
from .Model import Position
from .Generator.InitItems import generate_init_book, generate_init_user, generate_time_sequence, generate_donate_book
from .Generator.RandUtils import *
from .Exceptions.BadBehaviorException import BadQuery

class Core:
    def __init__(self, config: Dict[str, str]) -> None:
        self.java_path = config["Java-Path"]
        self.jar_path = config["Jar-Path"]

        self.books: Dict[Book, int] = generate_init_book()
        self.users: List[User] = generate_init_user()

        self.donates: List[Book] = generate_donate_book()

        self.dates: List[date] = generate_time_sequence()
        self.date_index = 0

        self.stored_movement: List[MoveRequest] = []
        self.rest_movement_count: int = 0
        self.rest_command_count: int = 0

        self.command: str = ""
        self.command_type = ""
        self.open: bool = True

        self.library = Library(self.books, self.users)

    def gen_init_command(self) -> List[str]:
        res = []
        res.append(str(len(self.books)))
        for b, c in self.books.items():
            res.append(f"{b} {c}")
        res.append(self.gen_command(CommandType.OPEN))
        self.command = res[-1]
        self.command_type = CommandType.OPEN
        self.open = True
        return res

    def command_callback(self, output: str):
        if self.rest_movement_count > 1:
            self.stored_movement.append(self.parse_move(output, self.command))
            self.rest_movement_count -= 1
            return Reaction(Action.Continue)
        elif self.rest_movement_count == 1:
            self.stored_movement.append(self.parse_move(output, self.command))
            # self.library.on_handle_move(self.dates[self.date_index], self.stored_movement, "open" if self.open else "close")
            self.rest_movement_count = 0
            if not self.open:
                self.library.on_close(self.dates[self.date_index], self.stored_movement)
                self.open = True
                return self.gen_open()
            else:
                self.library.on_open(self.dates[self.date_index], self.stored_movement, CommandInfo(self.command, "<OPEN CHECK>"))
            # Not Returned #
        elif output.isnumeric():
            self.rest_movement_count = int(output)
            if self.rest_movement_count > 0:
                return Reaction(Action.Continue)
            if not self.open:
                self.library.on_close(self.dates[self.date_index], [])
                self.open = True
                return self.gen_open()
            else:
                self.library.on_open(self.dates[self.date_index], [], CommandInfo(self.command, "<OPEN CHECK>"))
            # Not Returned #
        else:
            assert self.dates[self.date_index] == self.parse_date(output)
            self.parse_output(output, self.command)
            # Not Returned #
        # Gen Next Command
        if self.rest_command_count <= 0:
            self.open = False
            return self.gen_close()
        self.rest_command_count -= 1
        return self.gen_next_command()

    def before_open(self):
        self.rest_command_count = gen_int(15, 40)
        self.stored_movement = []

    def gen_next_command(self) -> Reaction:
        lent_book_cout = sum(map(lambda x: len(x.owned_book), (u for u in self.users)))
        order_book_cout = sum(map(lambda x: len(x.appoints), (u for u in self.users)))
        if probability(0.25):
            # Query Book or Credit
            if probability(0.7):
                user = pick_list(self.users)
                return Reaction(Action.SendText, self.gen_command(CommandType.QUERY_CREDIT, user_id=user.user_id))
            else:
                user = pick_list(self.users)
                book = pick_list(list(self.books.keys()))
                return Reaction(Action.SendText, self.gen_command(CommandType.QUERY, user_id=user.user_id, book_id=str(book)))
        elif lent_book_cout > len(self.users) * 2.5 or (lent_book_cout > 0 and probability(0.1)):
            # Return Or Renew
            while True:
                user = pick_list([u for u in self.users if len(u.owned_book) > 0])
                if len(user.owned_book) > 0:
                    break
            book: Book = pick_list(user.owned_book)
            if book in user.renewed_book:
                cmd_type = CommandType.RETURN
            else:
                return_date = book.return_date
                now_date = self.dates[self.date_index]
                if return_date is None:
                    cmd_type = CommandType.RETURN
                elif abs((return_date - now_date).days) <= 6 and probability(0.7):
                    cmd_type = CommandType.RENEW
                else:
                    cmd_type = CommandType.RETURN
            return Reaction(Action.SendText, self.gen_command(cmd_type, book_id=str(book), user_id=user.user_id))
        elif order_book_cout > len(self.users) or (order_book_cout > 0 and probability(0.3)):
            # Pick
            while True:
                user = pick_list([u for u in self.users if len(u.appoints) > 0])
                if len(user.appoints) > 0:
                    break
            order: Order = pick_list(user.appoints)
            return Reaction(Action.SendText, self.gen_command(CommandType.PICK, book_id=str(order.book), user_id=user.user_id))
        elif probability(0.6):
            # Order
            user = pick_list(self.users)
            book = pick_list(list(self.books.keys()))
            return Reaction(Action.SendText, self.gen_command(CommandType.ORDER, book_id=book, user_id=user.user_id))
        elif len(self.donates) > 0 and probability(0.5):
            # Donate
            user = pick_list(self.users)
            book = self.donates.pop()
            return Reaction(Action.SendText, self.gen_command(CommandType.DONATE, book_id=str(book), user_id=user.user_id))
        else:
            # Borrow
            user = pick_list(self.users)
            book = pick_list(list(self.books.keys()) + self.library.drift_corner)
            return Reaction(Action.SendText, self.gen_command(CommandType.BORROW, book_id=book, user_id=user.user_id))

    def gen_open(self) -> Reaction:
        self.date_index += 1
        if self.date_index >= len(self.dates):
            return Reaction(Action.Terminate)
        # Do every close check for credit change
        d = self.dates[self.date_index - 1] + timedelta(days=1)
        while d < self.dates[self.date_index]:
            self.library.handle_overdue_close(d)
            d += timedelta(days=1)
        self.before_open()
        return Reaction(Action.SendText, self.gen_command(CommandType.OPEN))

    def before_close(self):
        self.stored_movement = []
    
    def gen_close(self) -> Reaction:
        self.before_close()
        return Reaction(Action.SendText, self.gen_command(CommandType.CLOSE))

    def parse_output(self, s: str, command: str):
        command_info = CommandInfo(command, s)
        outputs = s.replace("not overdue", "NOD").replace("overdue", "OD").split()
        assert len(outputs) in [3, 5, 6]
        if len(outputs) == 3:
            # Query
            if '-' in outputs[1]:
                # Query Book
                book = Book.from_str(outputs[1])
                assert book is not None
                assert outputs[2].isnumeric()
                value = int(outputs[2])
                if value != self.library.book_shelf[book]:
                    raise BadQuery(command_info, f"Expected: {self.library.book_shelf[book]}, Got: {value}")
            else:
                # Query Credit
                user_id = outputs[1]
                assert any((user.user_id == user_id for user in self.users))
                try:
                    credit = int(outputs[2])
                except ValueError:
                    assert False
                for u in self.users:
                    if u.user_id == user_id:
                        break
                u.check_credit(command_info, credit)
        elif len(outputs) == 5:
            assert outputs[1] == '[accept]' or outputs[1] == '[reject]'
            accept = outputs[1] == '[accept]'
            user_id = outputs[2]
            assert any((user.user_id == user_id for user in self.users))
            book = Book.from_str(outputs[4])
            assert book is not None
            if outputs[3] == CommandType.BORROW.value:
                if accept:
                    self.library.on_accept_borrow(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
                else:
                    self.library.on_reject_borrow(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
            elif outputs[3] == CommandType.ORDER.value:
                if accept:
                    self.library.on_accept_order(NormalRequest(book, user_id, command_info))
                else:
                    self.library.on_reject_order(NormalRequest(book, user_id, command_info))
            elif outputs[3] == CommandType.PICK.value:
                if accept:
                    self.library.on_accept_pick(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
                else:
                    self.library.on_reject_pick(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
            elif outputs[3] == CommandType.RENEW.value:
                if accept:
                    self.library.on_accept_renew(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
                else:
                    self.library.on_reject_renew(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
            elif outputs[3] == CommandType.DONATE.value:
                self.library.on_donate(NormalRequest(book, user_id, command_info))
            else:
                assert False
        else:
            # Return
            assert outputs[1] == '[accept]'
            user_id = outputs[2]
            assert any((user.user_id == user_id for user in self.users))
            book = Book.from_str(outputs[4])
            assert book is not None
            assert outputs[5] in ["NOD", "OD"]
            overdue = outputs[5] == 'OD'
            self.library.on_return(NormalRequest(book, user_id, command_info), overdue, self.dates[self.date_index])

    def gen_command(self, cmd_type: CommandType, **kwargs):
        t = self.dates[self.date_index]
        if cmd_type == CommandType.OPEN or cmd_type == CommandType.CLOSE:
            command = f"[{t}] {cmd_type.value}"
        elif cmd_type == CommandType.QUERY_CREDIT:
            user_id = kwargs['user_id']
            command = f"[{t}] {user_id} {cmd_type.value}"
        else:
            book_id = kwargs['book_id']
            user_id = kwargs['user_id']
            command = f"[{t}] {user_id} {cmd_type.value} {book_id}"
        self.command = command
        self.command_type = cmd_type
        return command

    @staticmethod
    def parse_date(s: str) -> date:
        d = s.split()[0][1:11].split('-')  # ['2024', '01', '05']
        return date(
            year=int(d[0]),
            month=int(d[1]),
            day=int(d[2])
        )

    @staticmethod
    def parse_move(output: str, command: str) -> MoveRequest:
        command_info = CommandInfo(command, output)
        outputs = output.split()
        assert outputs[1] == 'move'
        assert len(outputs) == 9 or len(outputs) == 7
        book = Book.from_str(outputs[2])
        from_s = Position.from_str(outputs[4])
        to_s = Position.from_str(outputs[6])
        assert book is not None
        assert from_s is not None
        assert to_s is not None
        if len(outputs) == 7:
            return MoveRequest(command_info, (from_s, to_s), book)
        else:
            reserve_for = outputs[8]
            return MoveRequest(command_info, (from_s, to_s), book, reserve_for)

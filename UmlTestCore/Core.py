from typing import Dict, List
from datetime import date

from .Runner.Communicator import Reaction, Action
from .Manager.Request import MoveRequest, NormalRequest
from .Manager.Command import CommandInfo, CommandType
from .Model.Library import Library
from .Model.Book import Book
from .Model.User import User
from .Model import Position
from .Generator.InitItems import generate_init_book, generate_init_user, generate_time_sequence
from .Exceptions.BadBehaviorException import BadQuery

class Core:
    def __init__(self, config: Dict[str, str]) -> None:
        self.java_path = config["Java-Path"]
        self.jar_path = config["Jar-Path"]

        self.books: Dict[Book, int] = generate_init_book()
        self.users: List[User] = generate_init_user()

        self.dates: List[date] = generate_time_sequence()
        self.date_index = 0

        self.stored_movement: List[MoveRequest] = []
        self.rest_movement_count: int = 0

        self.command: str = ""
        self.command_type = ""
        self.open: bool = True

        self.library = Library(self.books, self.users)

    def gen_init_command(self) -> List[str]:
        res = []
        res.append(str(len(self.books)))
        for b, c in self.books.items():
            res.append(f"{b} {c}")
        res.append(self.gen_command(self.dates[self.date_index], CommandType.OPEN))
        self.command = res[-1]
        self.open = True
        return res

    def command_callback(self, output: str):
        if self.rest_movement_count > 1:
            self.stored_movement.append(self.parse_move(output, self.command))
            self.rest_movement_count -= 1
            return Reaction(Action.Continue)
        elif self.rest_movement_count == 1:
            self.stored_movement.append(self.parse_move(output, self.command))
            self.library.on_handle_move(self.dates[self.date_index], self.stored_movement, "open" if self.open else "close")
            self.rest_movement_count = 0
            if not open:
                self.date_index += 1
            if self.date_index >= len(self.dates):
                return Reaction(Action.Terminate)
            # Not Returned #
        elif output.isnumeric():
            self.rest_movement_count = int(output)
            return Reaction(Action.Continue)
        else:
            assert self.dates[self.date_index] == self.parse_date(output)
            self.parse_output(output, self.command)
            # Not Returned #
        # TODO: Gen Next Command

    def parse_output(self, s: str, command: str):
        command_info = CommandInfo(command, s)
        outputs = s.split()
        assert len(outputs) == 5 or len(outputs) == 3
        if len(outputs) == 3:
            # Query
            book = Book.from_str(outputs[1])
            assert book is not None
            assert outputs[2].isnumeric()
            value = int(outputs[2])
            if value != self.library.book_shelf[book]:
                raise BadQuery(command_info, f"Expected: {self.library.book_shelf[book]}, Got: {value}")
        else:
            assert outputs[1] == '[accept]' or outputs[1] == '[reject]'
            accept = outputs[1] == '[accept]'
            user_id = outputs[2]
            assert any((user.user_id == user_id for user in self.users))
            book = Book.from_str(outputs[1])
            assert book is not None
            if outputs[3] == CommandType.BORROW.value:
                if accept:
                    self.library.on_accept_borrow(NormalRequest(book, user_id, command_info))
                else:
                    self.library.on_reject_borrow(NormalRequest(book, user_id, command_info))
            elif outputs[3] == CommandType.ORDER.value:
                if accept:
                    self.library.on_accept_order(NormalRequest(book, user_id, command_info))
                else:
                    self.library.on_reject_order(NormalRequest(book, user_id, command_info))
            elif outputs[3] == CommandType.RETURN.value:
                assert accept
                self.library.on_return(NormalRequest(book, user_id, command_info))
            elif outputs[3] == CommandType.PICK.value:
                if accept:
                    self.library.on_accept_pick(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
                else:
                    self.library.on_reject_pick(NormalRequest(book, user_id, command_info), self.dates[self.date_index])
            else:
                assert False

    @staticmethod
    def gen_command(t: date, cmd_type: CommandType, **kwargs):
        if cmd_type == CommandType.OPEN or cmd_type == CommandType.CLOSE:
            return f"[{t}] {cmd_type.value}"
        book_id = kwargs['book_id']
        user_id = kwargs['user_id']
        return f"[{t}] {user_id} {cmd_type.value} {book_id}"

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

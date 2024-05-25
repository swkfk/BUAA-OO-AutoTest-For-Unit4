from typing import Tuple

from ..Model import Position
from ..Model.Book import Book
from .Command import CommandInfo


class MoveRequest:
    def __init__(self, command: CommandInfo, monvment: Tuple[Position, Position], book: Book, reserve_for: str = "") -> None:
        self.command: CommandInfo = command
        self.movement: Tuple[Position, Position] = monvment
        self.book: Book = book
        self.reserve_for: str = ""


class NormalRequest:
    def __init__(self, book: Book, user: str, command: CommandInfo) -> None:
        self.book: Book = book
        self.user_id: str = user
        self.command: CommandInfo = command

from ..Manager.Reserve import ReserveInfo

import enum

class Book:
    class Type(enum.Enum):
        A = 1
        B = 2
        C = 3

    def __init__(self, type: Type, id: str) -> None:
        self.type = type
        self.id = id
        self.reserve: ReserveInfo | None = None

    def reserveFor(self, reserve: ReserveInfo):
        self.reserve = reserve

    def __eq__(self, value: object) -> bool:
        if value is None or not isinstance(value, Book):
            return False
        return value.id == self.id and value.type == self.type

    def __str__(self) -> str:
        return f'{self.type.name}-{id}'

    def __hash__(self) -> int:
        return hash(str(self))

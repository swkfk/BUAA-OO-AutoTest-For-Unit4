from .User import User
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

    def reserve_for(self, reserve: ReserveInfo | None):
        self.reserve = reserve

    def is_reserved_for(self, user: User | str):
        if self.reserve is None:
            return False
        if isinstance(user, User):
            return user.user_id == self.reserve.user_id
        return user == self.reserve.user_id

    def __eq__(self, value: object) -> bool:
        if value is None or not isinstance(value, Book):
            return False
        return value.id == self.id and value.type == self.type

    def __str__(self) -> str:
        return f'{self.type.name}-{id}'

    def __hash__(self) -> int:
        return hash(str(self))

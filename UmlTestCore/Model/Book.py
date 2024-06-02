from ..Manager.Reserve import ReserveInfo

from datetime import date, timedelta
from enum import Enum
from typing import Literal

class Book:
    class Type(Enum):
        A = 1
        AU = 2
        B = 30
        C = 60
        BU = 7
        CU = 14

        def to_no_U(self):
            if self == Book.Type.AU:
                return Book.Type.A
            if self == Book.Type.BU:
                return Book.Type.B
            if self == Book.Type.CU:
                return Book.Type.C
            return self

    def __init__(self, type: Type, id: str) -> None:
        self.type = type
        self.id = id
        self.reserve: ReserveInfo | None = None
        self.return_date: date | None = None

    def reserve_for(self, reserve: ReserveInfo | None):
        self.reserve = reserve

    def is_reserved_for(self, user):
        if self.reserve is None:
            return False
        if isinstance(user, str):
            return user == self.reserve.user_id
        return user.user_id == self.reserve.user_id

    def reserve_overdue(self, now_date: date, time: Literal["open", "close"]):
        return self.reserve is not None and \
              (self.reserve.overdue_open(now_date) if time == "open" else self.reserve.overdue_close(now_date))

    def mark_borrow(self, now_date: date):
        self.return_date = now_date + timedelta(days=self.type.value)

    def set_renew(self):
        if self.return_date is not None:
            self.return_date += timedelta(days=30)

    def core_dump(self) -> str:
        base = f'{self.type.name}-{self.id}'
        if self.return_date is not None:
            base += f" (Return Due: {self.return_date})"
        return base
    
    def is_type_U(self) -> bool:
        return self.type in [Book.Type.AU, Book.Type.BU, Book.Type.CU, ]

    def __eq__(self, value: object) -> bool:
        if value is None or not isinstance(value, Book):
            return False
        return value.id == self.id and value.type == self.type

    def __str__(self) -> str:
        return f'{self.type.name}-{self.id}'

    def __hash__(self) -> int:
        return hash(str(self))

    @classmethod
    def from_str(cls, s: str):
        t, i = s.split('-')
        if t == 'A':
            return cls(cls.Type.A, i)
        elif t == 'B':
            return cls(cls.Type.B, i)
        elif t == 'C':
            return cls(cls.Type.C, i)
        elif t == 'AU':
            return cls(cls.Type.AU, i)
        elif t == 'BU':
            return cls(cls.Type.BU, i)
        elif t == 'CU':
            return cls(cls.Type.CU, i)

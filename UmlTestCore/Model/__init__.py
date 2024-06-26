from enum import Enum

class Position(Enum):
    BRO = "bro"
    AO = "ao"
    BS = "bs"
    BDC = "bdc"

    @classmethod
    def from_str(cls, s: str):
        if s == 'bro':
            return cls.BRO
        if s == 'ao':
            return cls.AO
        if s == 'bs':
            return cls.BS
        if s == 'bdc':
            return cls.BDC

from enum import Enum


class CommandType(Enum):
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'
    QUERY = 'queried'
    QUERY_CREDIT = 'queried credit score'
    BORROW = 'borrowed'
    ORDER = 'ordered'
    RETURN = 'returned'
    PICK = 'picked'
    RENEW = 'renewed'
    DONATE = 'donated'


class CommandInfo:
    def __init__(self, command: str, output: str) -> None:
        self.input: str = command
        self.output: str = output
    
    def __str__(self) -> str:
        return f"{{<stdout>: {self.output}, <stdin>: {self.input}}}"

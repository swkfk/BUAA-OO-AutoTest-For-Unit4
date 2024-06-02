from ..Manager.Command import CommandInfo

class BadBehavior(Exception):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        self.command: CommandInfo = command
        self.reason: str = reason
        self.prompt: str = "Bad Behavior"

    def __str__(self) -> str:
        if self.reason == "":
            return f"{self.prompt} {self.command}"
        return f"{self.prompt}({self.reason}) {self.command}"

    def __repr__(self) -> str:
        return "BadBehavior: " + str(self)


class BorrowInvalidBook(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Cannot borrow this book"


class OverdueBookRemained(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Overdue book not cleared"


class BookRemainedOnBro(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Book in the bro not cleared"

class BookRemainedInDrift(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Book in the bdc not cleared"

class BookMovementInvlid(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Book moved unexpectedly"


class BookPickInvlid(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Book picked unexpectedly"

class BadQuery(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Query wrong"

class BadReject(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "You shall not reject this"

class BadReturnOverdue(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Return overdue judgement is wrong"

class BadRenew(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Renew Error"

class DonatedBookInvalid(BadBehavior):
    def __init__(self, command: CommandInfo, reason: str = "") -> None:
        super().__init__(command, reason)
        self.prompt = "Drift Book Error"

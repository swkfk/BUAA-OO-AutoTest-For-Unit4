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


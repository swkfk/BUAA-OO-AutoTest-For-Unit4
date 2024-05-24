class Unexpected(Exception):
    def __init__(self, ident: str, reason: str) -> None:
        self.ident: str = ident
        self.reason: str = reason

    def __str__(self) -> str:
        return f"You shall not see this line! <I:{self.ident}, R:{self.reason}>"

    def __repr__(self) -> str:
        return "Unexpected: " + str(self)

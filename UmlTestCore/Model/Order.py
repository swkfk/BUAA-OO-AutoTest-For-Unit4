from .Book import Book

class Order:
    def __init__(self, user_id: str, book: Book) -> None:
        self.user_id: str = user_id
        self.book: Book = book

    def __eq__(self, value: object) -> bool:
        if value is None or not isinstance(value, Order):
            return False
        return self.user_id == value.user_id and self.book == value.book

    def __hash__(self) -> int:
        return hash(self.user_id + str(self.book))

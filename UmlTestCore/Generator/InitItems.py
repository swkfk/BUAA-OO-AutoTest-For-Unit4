from ..Model.Book import Book
from ..Model.User import User

import random
from datetime import date, timedelta

def generate_init_book():
    books = {}
    base_count = random.randint(2, 4)
    ids = random.sample(range(1000, 10000), k=base_count * 6)
    for i in range(0, base_count):
        books[Book(Book.Type.A, str(ids[i]))] = random.randint(1, 6)
    for i in range(base_count, base_count * 3):
        books[Book(Book.Type.B, str(ids[i]))] = random.randint(1, 6)
    for i in range(base_count * 3, base_count * 6):
        books[Book(Book.Type.C, str(ids[i]))] = random.randint(1, 6)
    return books

def generate_init_user():
    users = []
    count = random.randint(20, 40)
    ids = random.sample(range(1, 1000), k=count)
    for i in range(count):
        users.append(User(str(22370000 + ids[i])))
    return users

def generate_time_sequence():
    base_date = date(year=2024, month=1, day=1)

    count = random.randint(70, 100)
    offsets = random.sample(range(1, 366), k=count)

    offsets.sort()
    return [base_date + timedelta(days=offset) for offset in offsets]

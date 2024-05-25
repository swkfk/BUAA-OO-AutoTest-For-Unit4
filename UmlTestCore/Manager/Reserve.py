from datetime import date, timedelta

class ReserveInfo:
    def __init__(self, user_id: str, arrive_date: date) -> None:
        self.user_id: str = user_id

        # If arrived at the closing, the date shall be plus one day in caller
        self.arrive_date = arrive_date

    def overdue_open(self, now_date: date):
        return now_date - self.arrive_date >= timedelta(days=5)

    def overdue_close(self, now_date: date):
        return now_date - self.arrive_date >= timedelta(days=4)

    def __str__(self) -> str:
        return f"For {self.user_id} Arrive At {self.arrive_date}"

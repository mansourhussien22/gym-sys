from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class Membership:
    def __init__(
        self,
        membership_id: int,
        member_id: int,
        start_date: str,
        end_date: str,
        cost: float,
        total_sessions: int = 12,
        remaining_sessions: Optional[int] = None,
        is_frozen: bool = False,
        freeze_date: Optional[str] = None,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,  # لمنع أي خطأ إذا كانت محفوظة بالـ JSON
        **kwargs                       # لحماية السيستم من أي معاملات إضافية
    ):
        self._membership_id = int(membership_id)
        self._member_id = int(member_id)
        self.cost = float(cost)
        self.total_sessions = int(total_sessions)
        self.remaining_sessions = self.total_sessions if remaining_sessions is None else int(remaining_sessions)
        self.is_frozen = bool(is_frozen)
        self.freeze_date = freeze_date
        self._validate_and_set_dates(start_date, end_date)

    def _validate_and_set_dates(self, start_date: str, end_date: str) -> None:
        try:
            d_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            d_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Dates must follow the format 'YYYY-MM-DD'")

        if d_end < d_start:
            raise ValueError("End date must be after or equal to start date")

        self._start_date = start_date
        self._end_date = end_date

    @property
    def membership_id(self) -> int:
        return self._membership_id

    @property
    def member_id(self) -> int:
        return self._member_id

    @property
    def start_date(self) -> str:
        return self._start_date

    @property
    def end_date(self) -> str:
        return self._end_date

    @property
    def status(self) -> str:
        if self.is_frozen:
            return "Frozen"
        today = datetime.now().date()
        d_end = datetime.strptime(self._end_date, "%Y-%m-%d").date()
        if today > d_end or self.remaining_sessions <= 0:
            return "Expired"
        return "Active"

    @property
    def is_active(self) -> bool:
        return self.status == "Active"

    def freeze(self) -> None:
        if self.status != "Active":
            raise ValueError(f"Cannot freeze a membership that is {self.status}.")
        self.is_frozen = True
        self.freeze_date = datetime.now().strftime("%Y-%m-%d")

    def unfreeze(self) -> None:
        if not self.is_frozen or not self.freeze_date:
            raise ValueError("Membership is not currently frozen.")
        
        freeze_start = datetime.strptime(self.freeze_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        frozen_days = max(1, (today - freeze_start).days)

        current_end = datetime.strptime(self._end_date, "%Y-%m-%d").date()
        new_end = current_end + timedelta(days=frozen_days)
        self._end_date = new_end.strftime("%Y-%m-%d")

        self.is_frozen = False
        self.freeze_date = None

    def deduct_session(self) -> None:
        if self.remaining_sessions <= 0:
            raise ValueError("No remaining sessions left in this subscription.")
        self.remaining_sessions -= 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "membership_id": self.membership_id,
            "member_id": self.member_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "cost": self.cost,
            "total_sessions": self.total_sessions,
            "remaining_sessions": self.remaining_sessions,
            "is_frozen": self.is_frozen,
            "freeze_date": self.freeze_date,
            "status": self.status,
            "is_active": self.is_active
        }
from datetime import datetime
from typing import Optional, Dict, Any


class Payment:
    def __init__(
        self,
        payment_id: int,
        member_id: int,
        amount: float,
        method: str = "Cash",
        reference_number: Optional[str] = None,
        date: Optional[str] = None
    ):
        self._payment_id = int(payment_id)
        self._member_id = int(member_id)
        self.amount = float(amount)
        self.method = method or "Cash"
        self.reference_number = reference_number
        self._date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def payment_id(self) -> int:
        return self._payment_id

    @property
    def member_id(self) -> int:
        return self._member_id

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        if float(value) <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        self._amount = float(value)

    @property
    def date(self) -> str:
        return self._date

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "member_id": self.member_id,
            "amount": self.amount,
            "method": self.method,
            "reference_number": self.reference_number,
            "date": self.date
        }
from datetime import datetime
from typing import Dict, Any, Optional

VALID_PAYMENT_METHODS = {"Cash", "Visa", "Instapay", "Vodafone Cash"}


class Payment:
    def __init__(
        self,
        payment_id: int,
        member_id: int,
        amount: float,
        method: str = "Cash",
        reference_number: Optional[str] = None,
        **kwargs
    ):
        self._payment_id = int(payment_id)
        self._member_id = int(member_id)
        self.amount = float(amount)
        self.method = method
        self.reference_number = reference_number
        self.date = kwargs.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Payment method cannot be empty.")
        val = value.strip().title()
        matched = next((m for m in VALID_PAYMENT_METHODS if m.lower() == val.lower()), None)
        if not matched:
            raise ValueError(f"Invalid payment method '{value}'. Allowed: {', '.join(VALID_PAYMENT_METHODS)}")
        self._method = matched

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "member_id": self.member_id,
            "amount": self.amount,
            "method": self.method,
            "reference_number": self.reference_number,
            "date": self.date
        }
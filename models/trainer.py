import secrets
from typing import Dict, Any, Optional
from .person import Person


class Trainer(Person):
    ALLOWED_EXTRA = {"qr_token"}

    def __init__(
        self,
        person_id: int,
        name: str,
        phone: str,
        specialization: str,
        salary: float,
        qr_token: Optional[str] = None,
        **kwargs
    ):
        for k in kwargs:
            if k not in self.ALLOWED_EXTRA:
                raise TypeError(f"Trainer.__init__() got an unexpected keyword argument '{k}'")
        super().__init__(person_id, name, phone)
        self.specialization = specialization
        self.salary = float(salary)
        self.qr_token = qr_token or secrets.token_urlsafe(12)

    @property
    def specialization(self) -> str:
        return self._specialization

    @specialization.setter
    def specialization(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Specialization cannot be empty.")
        self._specialization = value.strip().title()

    @property
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, value: float) -> None:
        if float(value) < 0:
            raise ValueError("Salary cannot be negative.")
        self._salary = float(value)

    def get_details(self) -> str:
        return f"Trainer #{self.person_id} | Name: {self.name} | Phone: {self.phone} | Spec: {self.specialization} | Salary: ${self.salary:,.2f}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "person_id": self.person_id,
            "name": self.name,
            "phone": self.phone,
            "specialization": self.specialization,
            "salary": self.salary,
            "qr_token": self.qr_token
        }
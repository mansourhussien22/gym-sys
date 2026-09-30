from abc import ABC, abstractmethod
from typing import Dict, Any


class Person(ABC):
    def __init__(self, person_id: int, name: str, phone: str):
        self._person_id = int(person_id)
        self.name = name
        self.phone = phone

    @property
    def person_id(self) -> int:
        return self._person_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        cleaned = value.strip() if value else ""
        if len(cleaned) != 11 or not cleaned.isdigit() or not cleaned.startswith("01"):
            raise ValueError("Phone number must be an 11-digit mobile number starting with '01'")
        self._phone = cleaned

    @abstractmethod
    def get_details(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass
from abc import ABC, abstractmethod


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
        val = value.strip()
        if len(val) > 100:
            raise ValueError("Name cannot exceed 100 characters.")
        self._name = val

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Phone number cannot be empty.")
        val = value.strip()
        if not (val.isdigit() and len(val) == 11 and val.startswith("01")):
            raise ValueError("Phone number must be exactly 11 digits and start with '01'.")
        self._phone = val

    @abstractmethod
    def get_details(self) -> str:
        pass
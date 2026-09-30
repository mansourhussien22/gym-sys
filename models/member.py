import secrets
from datetime import datetime
from typing import Optional, Dict, Any, List
from .person import Person


class Member(Person):
    def __init__(
        self,
        person_id: int,
        name: str,
        phone: str,
        membership_type: str = "Standard",
        join_date: Optional[str] = None,
        trainer_id: Optional[int] = None,
        qr_token: Optional[str] = None,
        inbody_history: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        super().__init__(person_id, name, phone)
        self.membership_type = membership_type
        self._join_date = join_date or datetime.now().strftime("%Y-%m-%d")
        self.trainer_id = int(trainer_id) if trainer_id else None
        self.qr_token = qr_token or secrets.token_urlsafe(12)
        self.inbody_history = inbody_history or []

    @property
    def membership_type(self) -> str:
        return self._membership_type

    @membership_type.setter
    def membership_type(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Membership type cannot be empty.")
        self._membership_type = value.strip()

    @property
    def join_date(self) -> str:
        return self._join_date

    def add_inbody_record(self, weight: float, height: float, fat_percentage: float, muscle_mass: float, notes: str = "") -> Dict[str, Any]:
        w, h, f, m = float(weight), float(height), float(fat_percentage), float(muscle_mass)
        if w <= 0 or h <= 0 or f < 0 or m <= 0:
            raise ValueError("InBody metrics (weight, height, fat, muscle) must be positive values.")

        record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weight": round(w, 1),
            "height": round(h, 1),
            "fat_percentage": round(f, 1),
            "muscle_mass": round(m, 1),
            "notes": notes
        }
        self.inbody_history.append(record)
        return record

    def get_progress_summary(self) -> Dict[str, Any]:
        if not self.inbody_history:
            return {"status": "No InBody records available"}

        initial = self.inbody_history[0]
        latest = self.inbody_history[-1]

        w_init = initial.get("weight", 0.0)
        w_late = latest.get("weight", 0.0)
        f_init = initial.get("fat_percentage", 0.0)
        f_late = latest.get("fat_percentage", 0.0)
        m_init = initial.get("muscle_mass", 0.0)
        m_late = latest.get("muscle_mass", 0.0)

        return {
            "initial_record": initial,
            "latest_record": latest,
            "weight_change": round(w_late - w_init, 1),
            "fat_change": round(f_late - f_init, 1),
            "muscle_change": round(m_late - m_init, 1),
            "total_records": len(self.inbody_history)
        }

    def get_details(self) -> str:
        tr_info = f", Trainer ID: #{self.trainer_id}" if self.trainer_id else ", No Trainer"
        return f"Member #{self.person_id} | Name: {self.name} | Phone: {self.phone} | Plan: {self.membership_type}{tr_info}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "person_id": self.person_id,
            "name": self.name,
            "phone": self.phone,
            "membership_type": self.membership_type,
            "join_date": self.join_date,
            "trainer_id": self.trainer_id,
            "qr_token": self.qr_token,
            "inbody_history": self.inbody_history
        }
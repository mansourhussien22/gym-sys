from datetime import datetime
from typing import Optional, Dict, Any


class Attendance:
    def __init__(
        self,
        attendance_id: int,
        member_id: int,
        timestamp: Optional[str] = None
    ):
        self._attendance_id = int(attendance_id)
        self._member_id = int(member_id)
        self._timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def attendance_id(self) -> int:
        return self._attendance_id

    @property
    def member_id(self) -> int:
        return self._member_id

    @property
    def timestamp(self) -> str:
        return self._timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attendance_id": self.attendance_id,
            "member_id": self.member_id,
            "timestamp": self.timestamp
        }
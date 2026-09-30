import json
import os
from typing import Dict, Any


class FileManager:
    def __init__(self, filepath: str = "data/data.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            self._init_empty_file()

    def _init_empty_file(self) -> None:
        empty_data = {
            "members": [],
            "trainers": [],
            "memberships": [],
            "payments": [],
            "attendances": []
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(empty_data, f, ensure_ascii=False, indent=2)

    def load_data(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in ["members", "trainers", "memberships", "payments", "attendances"]:
                    if key not in data:
                        data[key] = []
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            self._init_empty_file()
            return self.load_data()

    def save_data(self, data: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
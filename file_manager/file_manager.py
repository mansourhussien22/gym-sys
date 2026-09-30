import os
import json
from typing import Dict, Any


class FileManager:
    def __init__(self, filepath: str = "data/data.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not os.path.exists(self.filepath):
            self._init_empty_file()

    def _init_empty_file(self) -> None:
        empty_data = {
            "members": [],
            "trainers": [],
            "memberships": [],
            "payments": [],
            "attendances": [],
            "body_metrics": []
        }
        self.save_data(empty_data)

    def load_data(self) -> Dict[str, Any]:
        self._ensure_file_exists()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {
                "members": [],
                "trainers": [],
                "memberships": [],
                "payments": [],
                "attendances": [],
                "body_metrics": []
            }

    def save_data(self, data: Dict[str, Any]) -> None:
        dir_name = os.path.dirname(self.filepath) or "."
        os.makedirs(dir_name, exist_ok=True)
        temp_file = os.path.join(dir_name, f".tmp_{os.path.basename(self.filepath)}")
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_file, self.filepath)
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

import os
import stat
import json
from typing import Dict, Any


class FileManager:
    def __init__(self, filepath: str = "data/data.json"):
        self.filepath = os.path.abspath(filepath)
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
        
        # إزالة خاصية Read-only برمجياً من الملف ومجلده إن وُجدت
        for target in [self.filepath, dir_name]:
            if os.path.exists(target):
                try:
                    os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
                except Exception:
                    pass

        # استخدام ملف مؤقت عادي بدون نقطة في البداية لتجنب قفل الويندوز
        temp_file = os.path.join(dir_name, f"temp_{os.path.basename(self.filepath)}")
        if os.path.exists(temp_file):
            try:
                os.chmod(temp_file, stat.S_IWRITE | stat.S_IREAD)
                os.remove(temp_file)
            except Exception:
                pass

        try:
            # محاولة الحفظ الآمن
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_file, self.filepath)
        except Exception:
            # لو فشل الاستبدال المؤقت، يتم الحفظ مباشرة في الملف الأصلي
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
"""
================================================================
 FitZone Pro - Comprehensive Bug Hunter & Test Suite
================================================================
 Usage:
     cd fitzone-pro
     python test_fitzone.py

 Outputs:
     - All bugs printed to terminal
     - bugs_found.json report
     - BUGS_REPORT.md report
================================================================
"""
import sys
import os
import json
import inspect
import re
import tempfile
import unittest
from datetime import datetime, timedelta


_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "models"))
sys.path.insert(0, os.path.join(_HERE, "services"))


try:
    from file_manager import FileManager
except ImportError as e:
    FileManager = None
    print(f"[WARN] file_manager import error: {e}")

try:
    from models import Person, Member, Trainer, Membership, Payment, Attendance
except ImportError as e:
    Person = Member = Trainer = Membership = Payment = Attendance = None
    print(f"[WARN] models import error: {e}")

try:
    from services import Gym, MEMBERSHIP_PLANS, QRManager
except ImportError as e:
    Gym = MEMBERSHIP_PLANS = QRManager = None
    print(f"[WARN] services import error: {e}")


BUGS_FOUND = []


def report_bug(code, severity, file, location, description, fix=""):
    BUGS_FOUND.append({
        "code": code,
        "severity": severity,
        "file": file,
        "location": location,
        "description": description,
        "fix": fix,
    })


# ================================================================
# Test 1: file_manager.py
# ================================================================
class TestFileManager(unittest.TestCase):
    def test_init_creates_body_metrics_key(self):
        if FileManager is None:
            return
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data.json")
            FileManager(path)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "body_metrics" not in data:
                report_bug(
                    "BUG-017", "Major", "file_manager.py",
                    "_init_empty_file()",
                    "Missing 'body_metrics' key in initial JSON",
                    'Add "body_metrics": [] to empty_data'
                )
            print(f"   -> Keys in data.json: {list(data.keys())}")

    def test_save_data_is_atomic(self):
        if FileManager is None:
            return
        src = inspect.getsource(FileManager.save_data)
        if "temp" not in src.lower() and "replace" not in src.lower():
            report_bug(
                "BUG-018", "Major", "file_manager.py",
                "save_data()",
                "Non-atomic write - file may corrupt on crash",
                "Write to temp then os.replace"
            )


# ================================================================
# Test 2: models/person.py
# ================================================================
class TestPerson(unittest.TestCase):
    def test_international_phone_rejected(self):
        if Person is None:
            return

        class DummyPerson(Person):
            def get_details(self): return ""
            def to_dict(self): return {}

        p1 = DummyPerson(1, "Ali", "01012345678")
        self.assertEqual(p1.phone, "01012345678")

        try:
            DummyPerson(2, "John", "+201012345678")
            report_bug(
                "BUG-013", "Major", "models/person.py",
                "phone.setter",
                "International phone numbers rejected",
                "Support +country code or use regex"
            )
        except ValueError:
            print("   -> International number correctly rejected")

    def test_name_max_length(self):
        if Person is None:
            return

        class DummyPerson(Person):
            def get_details(self): return ""
            def to_dict(self): return {}

        huge = "A" * 100000
        try:
            p = DummyPerson(1, huge, "01012345678")
            if len(p.name) == 100000:
                report_bug(
                    "BUG-014", "Minor", "models/person.py",
                    "name.setter",
                    "No max length - 100k chars stored",
                    "Limit to 100 chars"
                )
        except ValueError:
            print("   -> Long name correctly rejected")


# ================================================================
# Test 3: models/member.py
# ================================================================
class TestMember(unittest.TestCase):
    def test_negative_inbody_values(self):
        if Member is None:
            return
        m = Member(10001, "Test", "01012345678")
        try:
            m.add_inbody_record(weight=-70, height=-180,
                                fat_percentage=-5, muscle_mass=-30)
            report_bug(
                "BUG-011", "Major", "models/member.py",
                "add_inbody_record()",
                "Negative InBody values accepted",
                "Raise ValueError if any value <= 0"
            )
        except ValueError:
            print("   -> Negative values correctly rejected")

    def test_progress_summary_missing_keys(self):
        if Member is None:
            return
        m = Member(10001, "Test", "01012345678")
        m.inbody_history = [{"date": "2025-01-01"}]
        try:
            summary = m.get_progress_summary()
            print(f"   -> Summary OK: {summary}")
        except KeyError as e:
            report_bug(
                "BUG-012", "Major", "models/member.py",
                "get_progress_summary()",
                f"KeyError on missing key {e}",
                "Use .get() with defaults"
            )


# ================================================================
# Test 4: models/membership.py
# ================================================================
class TestMembership(unittest.TestCase):
    def test_unfreeze_same_day(self):
        if Membership is None:
            return
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        ms = Membership(1, 10001, today, future, 600.0, total_sessions=24)
        ms.freeze()
        ms.unfreeze()
        original_end = datetime.strptime(future, "%Y-%m-%d").date()
        new_end = datetime.strptime(ms.end_date, "%Y-%m-%d").date()
        diff = (new_end - original_end).days
        if diff > 0:
            report_bug(
                "BUG-008", "Major", "models/membership.py",
                "unfreeze()",
                f"Same-day unfreeze added {diff} free day(s)",
                "Remove max(1, ...) when diff is 0"
            )

    def test_remaining_sessions_out_of_bounds(self):
        if Membership is None:
            return
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        ms = Membership(1, 10001, today, future, 600.0,
                        total_sessions=24, remaining_sessions=1000)
        if ms.remaining_sessions > ms.total_sessions:
            report_bug(
                "BUG-010", "Minor", "models/membership.py",
                "__init__",
                f"remaining ({ms.remaining_sessions}) > total ({ms.total_sessions})",
                "Clamp remaining between 0 and total"
            )


# ================================================================
# Test 5: models/payment.py
# ================================================================
class TestPayment(unittest.TestCase):
    def test_invalid_method(self):
        if Payment is None:
            return
        p = Payment(1, 10001, 500.0, method="BITCOIN")
        if p.method == "BITCOIN":
            report_bug(
                "BUG-047", "Minor", "models/payment.py",
                "__init__",
                "Any string accepted as payment method",
                "Whitelist: Cash, Visa, Instapay, Vodafone Cash"
            )


# ================================================================
# Test 6: models/trainer.py
# ================================================================
class TestTrainer(unittest.TestCase):
    def test_kwargs_swallows_typos(self):
        if Trainer is None:
            return
        try:
            Trainer(20001, "Coach", "01012345678",
                    "Iron", 6000.0,
                    specializatoin="TYPO")
            report_bug(
                "BUG-049", "Minor", "models/trainer.py",
                "__init__",
                "**kwargs hides parameter typos",
                "Remove **kwargs or validate keys"
            )
        except TypeError:
            print("   -> Typo correctly rejected")


# ================================================================
# Test 7: services/qr_manager.py
# ================================================================
class TestQRManager(unittest.TestCase):
    def test_qr_filename_collision(self):
        if QRManager is None:
            return
        src = inspect.getsource(QRManager.generate_qr)
        if "member_" in src and "trainer_" not in src:
            report_bug(
                "BUG-015", "Critical", "services/qr_manager.py",
                "generate_qr()",
                "Filename 'member_{id}.png' collides between roles",
                "Use 'user_{id}.png' or role prefix"
            )

    def test_webcam_in_headless(self):
        if QRManager is None:
            return
        src = inspect.getsource(QRManager.scan_from_webcam)
        if "imshow" in src or "namedWindow" in src:
            report_bug(
                "BUG-016", "Major", "services/qr_manager.py",
                "scan_from_webcam()",
                "Uses cv2.imshow - fails on headless servers",
                "Separate desktop GUI from server code"
            )


# ================================================================
# Test 8: services/gym_service.py
# ================================================================
class TestGymService(unittest.TestCase):
    def _make_gym(self):
        if Gym is None or FileManager is None:
            return None
        tmp = tempfile.mkdtemp()
        fm = FileManager(os.path.join(tmp, "d.json"))
        return Gym(file_manager=fm)

    def test_cost_bypass(self):
        g = self._make_gym()
        if g is None:
            return
        try:
            g.register_member("Ali", "01012345678",
                              "Fitness (Full Month - 30 Days)")
            m = g.members[0]
            g.memberships.clear()
            membership = g.create_membership_with_plan(
                m.person_id, "Fitness (Full Month - 30 Days)",
                cost_entered=1.0
            )
            if membership.cost == 1.0:
                report_bug(
                    "BUG-001", "Critical", "services/gym_service.py",
                    "create_membership_with_plan()",
                    "Any cost is accepted without checking plan price",
                    "Validate cost == MEMBERSHIP_PLANS[plan]['price']"
                )
        except ValueError:
            print("   -> Cost mismatch correctly rejected")

    def test_invalid_plan_keyerror(self):
        g = self._make_gym()
        if g is None:
            return
        try:
            g.register_member("Ali", "01012345678", "FAKE_PLAN")
        except KeyError as e:
            report_bug(
                "BUG-002", "Major", "services/gym_service.py",
                "register_member()",
                f"Invalid plan raises KeyError instead of ValueError ({e})",
                "Check plan in MEMBERSHIP_PLANS first"
            )
        except ValueError:
            print("   -> Invalid plan correctly rejected with ValueError")

    def test_trainer_phone_duplicate(self):
        if Gym is None or Trainer is None:
            return
        g = self._make_gym()
        if g is None:
            return
        t1 = Trainer(20001, "Coach A", "01011111111", "Iron", 5000)
        t2 = Trainer(20002, "Coach B", "01011111111", "Cardio", 5000)
        g.add_trainer(t1)
        try:
            g.add_trainer(t2)
            report_bug(
                "BUG-006", "Major", "services/gym_service.py",
                "add_trainer()",
                "Duplicate trainer phone number accepted",
                "Check phone uniqueness like members"
            )
        except ValueError:
            print("   -> Duplicate phone correctly rejected")

    def test_sequential_ids(self):
        if Gym is None:
            return
        src = inspect.getsource(Gym.generate_member_id)
        if "random.randint" in src:
            report_bug(
                "BUG-019", "Major", "services/gym_service.py",
                "generate_member_id()",
                "Uses random.randint - high collision chance",
                "max(existing_ids, default=10000) + 1"
            )


# ================================================================
# Test 9: server.py static analysis
# ================================================================
class TestServer(unittest.TestCase):
    def test_no_auth(self):
        if not os.path.exists("server.py"):
            print("   -> server.py not found")
            return
        with open("server.py", "r", encoding="utf-8") as f:
            src = f.read()
        if "login_required" not in src and "jwt" not in src.lower() and "@require_login" not in src:
            report_bug(
                "BUG-021", "Critical", "server.py",
                "All API routes",
                "No authentication - anyone can modify data",
                "Add JWT or Flask-Login"
            )

    def test_requirements_missing_customtkinter(self):
        if not os.path.exists("requirements.txt"):
            return
        with open("requirements.txt") as f:
            content = f.read().lower()
        if "customtkinter" not in content:
            report_bug(
                "BUG-038", "Critical", "requirements.txt",
                "Full file",
                "customtkinter missing but used by gui/app.py",
                "Add customtkinter"
            )

    def test_opencv_headless(self):
        if not os.path.exists("requirements.txt"):
            return
        with open("requirements.txt") as f:
            content = f.read()
        if "opencv-python-headless" in content:
            report_bug(
                "BUG-039", "Critical", "requirements.txt",
                "Full file",
                "opencv-python-headless lacks GUI - desktop app fails",
                "Replace with opencv-python"
            )

    def test_no_cors(self):
        if not os.path.exists("server.py"):
            return
        with open("server.py", "r", encoding="utf-8") as f:
            src = f.read()
        if "CORS" not in src:
            report_bug(
                "BUG-040", "Major", "server.py",
                "app = Flask(__name__)",
                "No CORS - frontend from other origin fails",
                "Add flask-cors and CORS(app)"
            )


# ================================================================
# Test 10: index.html static analysis
# ================================================================
class TestFrontend(unittest.TestCase):
    def _get_html_path(self):
        if os.path.exists("templates/index.html"):
            return "templates/index.html"
        if os.path.exists("index.html"):
            return "index.html"
        return None

    def test_template_literal_quotes(self):
        path = self._get_html_path()
        if not path:
            print("   -> index.html not found")
            return
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        patterns = [
            r"onclick=\"[^\"]*'\$\{[^}]*\.name\}'",
            r"onclick=\"[^\"]*'\$\{[^}]*\.ref\}'",
        ]
        for p in patterns:
            if re.search(p, src):
                report_bug(
                    "BUG-030/031", "Critical", path,
                    "Template literals",
                    "Names placed in '...' inside onclick - breaks on quotes",
                    "Use JSON.stringify() or escape"
                )
                return
        print("   -> No template literal quote issues")

    def test_exit_destroys_body(self):
        path = self._get_html_path()
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        if "document.body.innerHTML =" in src:
            report_bug(
                "BUG-033", "Major", path,
                "exitApplication()",
                "Wipes body.innerHTML - loses event listeners",
                "Use a modal overlay instead"
            )


# ================================================================
# Test 11: data.json integrity
# ================================================================
class TestDataIntegrity(unittest.TestCase):
    def _get_data_path(self):
        if os.path.exists(os.path.join("data", "data.json")):
            return os.path.join("data", "data.json")
        if os.path.exists("data.json"):
            return "data.json"
        return None

    def test_members_without_payment(self):
        path = self._get_data_path()
        if not path:
            print("   -> data.json not found")
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        paid_ids = {p["member_id"] for p in data.get("payments", [])}
        sub_members = {ms["member_id"] for ms in data.get("memberships", [])}
        missing = sub_members - paid_ids
        if missing:
            report_bug(
                "BUG-041", "Critical", "data/data.json",
                "payments[]",
                f"Members {missing} have memberships but no payments",
                "Add a payment for each membership"
            )

    def test_future_dates(self):
        path = self._get_data_path()
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        today = datetime.now().date()
        for m in data.get("members", []):
            try:
                jd = datetime.strptime(m.get("join_date", "2000-01-01"), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
            if jd > today:
                report_bug(
                    "BUG-043", "Major", "data/data.json",
                    f"member {m['person_id']}",
                    f"Join date in the future: {jd}",
                    "Use a valid date"
                )
                return


# ================================================================
# Test 12: Architecture
# ================================================================
class TestArchitecture(unittest.TestCase):
    def test_no_threading_lock(self):
        if not os.path.exists("file_manager.py"):
            return
        with open("file_manager.py", "r", encoding="utf-8") as f:
            src = f.read()
        if "Lock" not in src and "threading" not in src:
            report_bug(
                "BUG-056", "Major", "file_manager.py",
                "save_data()",
                "No lock for concurrent writes",
                "Use threading.Lock"
            )

    def test_json_not_encrypted(self):
        if not os.path.exists("data/data.json") and not os.path.exists("data.json"):
            return
        report_bug(
            "BUG-057", "Major", "data/data.json",
            "Full file",
            "Sensitive data (payments, salaries) not encrypted",
            "Encrypt file or use a database"
        )

    def test_no_pagination(self):
        if not os.path.exists("server.py"):
            return
        with open("server.py", "r", encoding="utf-8") as f:
            src = f.read()
        if "limit" not in src and "page" not in src:
            report_bug(
                "BUG-058", "Major", "server.py",
                "/api/members, /api/payments",
                "No pagination - all data returned at once",
                "Add ?page=N&limit=M"
            )

    def test_no_logging(self):
        if not os.path.exists("server.py"):
            return
        with open("server.py", "r", encoding="utf-8") as f:
            src = f.read()
        if "logging" not in src and "logger" not in src:
            report_bug(
                "BUG-059", "Major", "server.py",
                "All operations",
                "No logging of sensitive operations",
                "Use logging module"
            )


# ================================================================
# Report generators
# ================================================================
def generate_markdown_report():
    lines = ["# FitZone Pro - Comprehensive Bug Report\n\n"]
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    lines.append(f"**Total Bugs:** {len(BUGS_FOUND)}\n\n---\n\n")

    for sev in ["Critical", "Major", "Minor"]:
        group = [b for b in BUGS_FOUND if b["severity"] == sev]
        if not group:
            continue
        lines.append(f"## {sev} ({len(group)})\n\n")
        for b in group:
            lines.append(f"### [{b['code']}] {b['description'][:60]}\n")
            lines.append(f"- **File:** `{b['file']}`\n")
            lines.append(f"- **Location:** `{b['location']}`\n")
            lines.append(f"- **Issue:** {b['description']}\n")
            if b["fix"]:
                lines.append(f"- **Fix:** {b['fix']}\n")
            lines.append("\n")
        lines.append("---\n\n")

    with open("BUGS_REPORT.md", "w", encoding="utf-8") as f:
        f.write("".join(lines))


def generate_json_report():
    with open("bugs_found.json", "w", encoding="utf-8") as f:
        json.dump(BUGS_FOUND, f, ensure_ascii=False, indent=2)


# ================================================================
# Main
# ================================================================
def main():
    print("\n" + "=" * 70)
    print("  FitZone Pro - Bug Hunter & Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    result = runner.run(suite)

    print(f"\n  Tests run: {result.testsRun}")
    print(f"  Passed:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed:    {len(result.failures)}")
    print(f"  Errors:    {len(result.errors)}")

    print("\n" + "=" * 70)
    print("  BUG HUNT RESULTS")
    print("=" * 70)

    if not BUGS_FOUND:
        print("\n  No bugs detected. Code is clean!\n")
    else:
        critical = [b for b in BUGS_FOUND if b["severity"] == "Critical"]
        major = [b for b in BUGS_FOUND if b["severity"] == "Major"]
        minor = [b for b in BUGS_FOUND if b["severity"] == "Minor"]

        print(f"\n  Critical: {len(critical)}")
        print(f"  Major:    {len(major)}")
        print(f"  Minor:    {len(minor)}")
        print(f"  Total:    {len(BUGS_FOUND)}")

        for label, group in [
            ("CRITICAL", critical),
            ("MAJOR", major),
            ("MINOR", minor),
        ]:
            if not group:
                continue
            print(f"\n{'-' * 70}")
            print(f"  {label} BUGS ({len(group)})")
            print(f"{'-' * 70}")
            for b in group:
                print(f"\n  [{b['code']}]")
                print(f"  File: {b['file']} -> {b['location']}")
                print(f"  Issue: {b['description']}")
                if b["fix"]:
                    print(f"  Fix: {b['fix']}")

    generate_markdown_report()
    generate_json_report()

    print("\n" + "=" * 70)
    print("  Reports Generated")
    print("=" * 70)
    print("  bugs_found.json")
    print("  BUGS_REPORT.md")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
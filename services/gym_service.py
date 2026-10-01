from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from models import Member, Trainer, Membership, Payment, Attendance
from file_manager import FileManager

try:
    from .qr_manager import QRManager
except ImportError:
    try:
        from services.qr_manager import QRManager
    except ImportError:
        from qr_manager import QRManager

MEMBERSHIP_PLANS = {
    "Fitness (Full Month - 30 Days)": {
        "days": 30, "sessions": 24, "price": 600.0, "category": "Fitness Only"
    },
    "Fitness (Half Month - 15 Days)": {
        "days": 15, "sessions": 12, "price": 350.0, "category": "Fitness Only"
    },
    "Fitness + Cardio (Full Month - 30 Days)": {
        "days": 30, "sessions": 26, "price": 900.0, "category": "Fitness + Cardio"
    },
    "Fitness + Cardio (Half Month - 15 Days)": {
        "days": 15, "sessions": 14, "price": 550.0, "category": "Fitness + Cardio"
    },
    "Annual VIP (All Access - 365 Days)": {
        "days": 365, "sessions": 300, "price": 4500.0, "category": "VIP All-Access"
    },
}

TRAINER_TAX_RATE = 0.10


class Gym:
    def __init__(self, file_manager: Optional[FileManager] = None):
        self.file_manager = file_manager or FileManager("data/data.json")
        self.members: List[Member] = []
        self.trainers: List[Trainer] = []
        self.memberships: List[Membership] = []
        self.payments: List[Payment] = []
        self.attendances: List[Attendance] = []
        self.load()

    def load(self) -> None:
        data = self.file_manager.load_data()
        self.members = [Member(**m) for m in data.get("members", [])]
        self.trainers = [Trainer(**t) for t in data.get("trainers", [])]
        self.memberships = [Membership(**ms) for ms in data.get("memberships", [])]
        self.payments = [Payment(**p) for p in data.get("payments", [])]
        self.attendances = [Attendance(**a) for a in data.get("attendances", [])]

    def save(self) -> None:
        data = {
            "members": [m.to_dict() for m in self.members],
            "trainers": [t.to_dict() for t in self.trainers],
            "memberships": [ms.to_dict() for ms in self.memberships],
            "payments": [p.to_dict() for p in self.payments],
            "attendances": [a.to_dict() for a in self.attendances]
        }
        self.file_manager.save_data(data)

    def generate_member_id(self) -> int:
        return max([m.person_id for m in self.members], default=10000) + 1

    def generate_trainer_id(self) -> int:
        return max([t.person_id for t in self.trainers], default=20000) + 1

    def register_member(
        self,
        name: str,
        phone: str,
        plan_name: str,
        payment_method: str = "Cash",
        trainer_id: Optional[int] = None,
        weight: Optional[float] = None,
        height: Optional[float] = None,
        fat_percentage: Optional[float] = None,
        muscle_mass: Optional[float] = None
    ) -> Member:
        phone_match = self.find_member_by_phone(phone)
        if phone_match:
            raise ValueError(f"Phone '{phone}' is already registered to '{phone_match.name}'.")

        member_id = self.generate_member_id()
        member = Member(
            person_id=member_id,
            name=name,
            phone=phone,
            membership_type=plan_name,
            trainer_id=int(trainer_id) if trainer_id else None
        )

        if all(v is not None for v in [weight, height, fat_percentage, muscle_mass]):
            member.add_inbody_record(weight, height, fat_percentage, muscle_mass, notes="Initial Registration InBody")

        self.members.append(member)
        QRManager.generate_qr(member.person_id, member.qr_token, role="member")
        self.create_membership_with_plan(member_id=member.person_id, plan_name=plan_name, payment_method=payment_method)
        self.save()
        return member

    def add_member(self, member: Member) -> None:
        if self.find_member_by_id(member.person_id):
            raise ValueError(f"Member ID #{member.person_id} is already taken.")
        phone_match = self.find_member_by_phone(member.phone)
        if phone_match:
            raise ValueError(f"Phone '{member.phone}' is already registered to '{phone_match.name}'.")

        self.members.append(member)
        QRManager.generate_qr(member.person_id, member.qr_token, role="member")
        self.save()

    def update_member(self, member_id: int, name: str, phone: str, membership_type: str) -> None:
        member = self.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member #{member_id} not found.")

        for m in self.members:
            if m.phone == phone and int(m.person_id) != int(member_id):
                raise ValueError(f"Phone number '{phone}' is already registered to '{m.name}'.")

        member.name = name
        member.phone = phone
        member.membership_type = membership_type
        self.save()

    def delete_member(self, member_id: int) -> None:
        member = self.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member #{member_id} not found.")

        self.members = [m for m in self.members if int(m.person_id) != int(member_id)]
        self.memberships = [ms for ms in self.memberships if int(ms.member_id) != int(member_id)]
        self.payments = [p for p in self.payments if int(p.member_id) != int(member_id)]
        self.attendances = [a for a in self.attendances if int(a.member_id) != int(member_id)]
        self.save()

    def find_member_by_id(self, member_id: int) -> Optional[Member]:
        return next((m for m in self.members if int(m.person_id) == int(member_id)), None)

    def find_member_by_phone(self, phone: str) -> Optional[Member]:
        return next((m for m in self.members if m.phone == phone), None)

    def find_member_by_token(self, token: str) -> Optional[Member]:
        return next((m for m in self.members if getattr(m, "qr_token", None) == token), None)

    def search_members(self, query: str) -> List[Member]:
        q = query.strip().lower()
        return [m for m in self.members if q in m.name.lower() or q in str(m.person_id) or q in m.phone]

    def filter_members_by_status(self, active: bool = True) -> List[Member]:
        return [m for m in self.members if (self.get_active_membership(m.person_id) is not None) == active]

    def add_trainer(self, trainer: Trainer) -> None:
        if any(int(t.person_id) == int(trainer.person_id) for t in self.trainers):
            raise ValueError(f"Trainer ID #{trainer.person_id} already exists.")
        if any(t.phone == trainer.phone for t in self.trainers) or any(m.phone == trainer.phone for m in self.members):
            raise ValueError(f"Phone '{trainer.phone}' is already registered in the system.")
        self.trainers.append(trainer)
        token = getattr(trainer, "qr_token", str(trainer.person_id))
        QRManager.generate_qr(trainer.person_id, token, role="trainer")
        self.save()

    def find_trainer_by_id(self, trainer_id: int) -> Optional[Trainer]:
        return next((t for t in self.trainers if int(t.person_id) == int(trainer_id)), None)

    def find_trainer_by_token(self, token: str) -> Optional[Trainer]:
        return next((t for t in self.trainers if getattr(t, "qr_token", None) == token), None)

    def assign_trainer(self, member_id: int, trainer_id: int) -> None:
        member = self.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member #{member_id} not found.")
        trainer = self.find_trainer_by_id(trainer_id)
        if not trainer:
            raise ValueError(f"Trainer #{trainer_id} not found.")
        member.trainer_id = int(trainer_id)
        self.save()

    def get_trainer_full_profile(self, trainer_id: int) -> Dict[str, Any]:
        self.load()
        trainer = self.find_trainer_by_id(trainer_id)
        if not trainer:
            raise ValueError(f"Trainer #{trainer_id} not found.")

        att_logs = [a for a in self.attendances if int(a.member_id) == int(trainer_id)]
        last_checkin = att_logs[-1].timestamp if att_logs else "Never"

        currently_in = any(
            int(p["person_id"]) == int(trainer_id) for p in self.get_currently_in_gym() if p.get("role") == "Trainer"
        )
        trainees_report = self.get_trainer_trainees_report(trainer_id)

        return {
            "id": trainer.person_id,
            "name": trainer.name,
            "phone": trainer.phone,
            "specialization": trainer.specialization,
            "salary": trainer.salary,
            "qr_token": getattr(trainer, "qr_token", ""),
            "total_attendance_days": len(att_logs),
            "last_checkin": last_checkin,
            "is_present_now": currently_in,
            "total_trainees": trainees_report["total_trainees"],
            "trainees": trainees_report["trainees"]
        }

    def get_trainer_trainees_report(self, trainer_id: int) -> Dict[str, Any]:
        self.load()
        trainer = self.find_trainer_by_id(trainer_id)
        if not trainer:
            raise ValueError(f"Trainer #{trainer_id} not found.")

        # تأكيد المقارنة بالأرقام الصريحة لمنع تداخل المتدربين بين الكباتن
        trainees = [
            m for m in self.members 
            if m.trainer_id is not None and int(m.trainer_id) == int(trainer_id)
        ]
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)

        report = []
        for m in trainees:
            att_3m = [
                a for a in self.attendances
                if int(a.member_id) == int(m.person_id) and datetime.strptime(a.timestamp[:10], "%Y-%m-%d") >= three_months_ago
            ]
            sub = self.get_latest_membership(m.person_id)

            # تفاصيل أول فحص وآخر فحص لمقارنة التطور الفعلي
            prog = {"has_data": False}
            if hasattr(m, "inbody_history") and m.inbody_history:
                initial = m.inbody_history[0]
                latest = m.inbody_history[-1]

                try:
                    d_start = datetime.strptime(initial.get("date", ""), "%Y-%m-%d").date()
                    d_end = datetime.strptime(latest.get("date", ""), "%Y-%m-%d").date()
                    tracked_days = max(1, (d_end - d_start).days) if d_end != d_start else 0
                except Exception:
                    tracked_days = 0

                w_init = initial.get("weight", 0.0)
                w_late = latest.get("weight", 0.0)
                f_init = initial.get("fat_percentage", 0.0)
                f_late = latest.get("fat_percentage", 0.0)
                m_init = initial.get("muscle_mass", 0.0)
                m_late = latest.get("muscle_mass", 0.0)

                prog = {
                    "has_data": True,
                    "first_day_date": initial.get("date", "N/A"),
                    "latest_date": latest.get("date", "N/A"),
                    "tracked_days": tracked_days,
                    "total_scans": len(m.inbody_history),
                    "initial": {"weight": w_init, "fat": f_init, "muscle": m_init, "height": initial.get("height", 0.0)},
                    "latest": {"weight": w_late, "fat": f_late, "muscle": m_late, "height": latest.get("height", 0.0)},
                    "weight_change": round(w_late - w_init, 1),
                    "fat_change": round(f_late - f_init, 1),
                    "muscle_change": round(m_late - m_init, 1)
                }

            report.append({
                "member_id": m.person_id,
                "name": m.name,
                "phone": m.phone,
                "attendance_last_3_months": len(att_3m),
                "remaining_sessions": getattr(sub, "remaining_sessions", 0) if sub else 0,
                "status": getattr(sub, "status", "Expired") if sub else "No Subscription",
                "progress_before_and_after": prog
            })

        return {
            "trainer_name": trainer.name,
            "specialization": trainer.specialization,
            "total_trainees": len(trainees),
            "trainees": report
        }

    def calculate_plan_cost(self, plan_name: str, has_trainer: bool) -> float:
        if plan_name not in MEMBERSHIP_PLANS:
            raise ValueError(f"Invalid plan selected: '{plan_name}'")
        base = MEMBERSHIP_PLANS[plan_name]["price"]
        if has_trainer:
            return round(base * (1.0 + TRAINER_TAX_RATE), 2)
        return round(base, 2)

    def create_membership_with_plan(
        self,
        member_id: int,
        plan_name: str,
        cost_entered: Optional[float] = None,
        payment_method: str = "Cash"
    ) -> Membership:
        if plan_name not in MEMBERSHIP_PLANS:
            raise ValueError(f"Invalid plan selected: '{plan_name}'")

        member = self.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member #{member_id} does not exist.")

        if self.get_active_membership(member_id):
            raise ValueError(f"Member #{member_id} already has an active subscription. Use renew instead.")

        has_trainer = member.trainer_id is not None
        official_cost = self.calculate_plan_cost(plan_name, has_trainer)

        if cost_entered is not None and round(float(cost_entered), 2) != official_cost:
            raise ValueError(f"Invalid plan cost: entered ${cost_entered}, expected ${official_cost}")

        final_cost = official_cost
        plan_info = MEMBERSHIP_PLANS[plan_name]
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=plan_info["days"])
        sessions = plan_info.get("sessions", 12)

        next_id = max([ms.membership_id for ms in self.memberships], default=0) + 1
        
        membership = Membership(
            membership_id=next_id,
            member_id=int(member_id),
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            cost=final_cost,
            total_sessions=sessions,
            remaining_sessions=sessions
        )

        member.membership_type = plan_name
        self.memberships.append(membership)
        self.record_payment(int(member_id), final_cost, method=payment_method, ref="Plan Enrollment")
        self.save()
        return membership

    def renew_membership(
        self,
        member_id: int,
        plan_name: str,
        payment_method: str = "Cash",
        weight: Optional[float] = None,
        height: Optional[float] = None,
        fat_percentage: Optional[float] = None,
        muscle_mass: Optional[float] = None
    ) -> Membership:
        self.load()
        member = self.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member #{member_id} does not exist.")

        if plan_name not in MEMBERSHIP_PLANS:
            raise ValueError(f"Invalid plan selected: '{plan_name}'")

        # معالجة الـ InBody بمرونة: استرجاع الطول السابق تلقائياً لو تُرك فارغاً
        if weight is not None and float(weight) > 0:
            h_val = float(height) if height and float(height) > 0 else None
            if not h_val:
                if hasattr(member, "inbody_history") and member.inbody_history:
                    h_val = member.inbody_history[-1].get("height", 170.0)
                else:
                    h_val = 170.0

            f_val = float(fat_percentage) if fat_percentage is not None and float(fat_percentage) >= 0 else 20.0
            m_val = float(muscle_mass) if muscle_mass is not None and float(muscle_mass) > 0 else 30.0

            member.add_inbody_record(
                weight=float(weight),
                height=h_val,
                fat_percentage=f_val,
                muscle_mass=m_val,
                notes="Renewal InBody Progress"
            )

        plan_info = MEMBERSHIP_PLANS[plan_name]
        has_trainer = member.trainer_id is not None
        cost = self.calculate_plan_cost(plan_name, has_trainer)

        # التجديد الآمن: إذا كان الاشتراك منتهياً يبدأ فوراً من تاريخ اليوم
        today = datetime.now().date()
        active_sub = self.get_active_membership(member_id)

        if active_sub and getattr(active_sub, "status", "") == "Active":
            try:
                curr_end = datetime.strptime(active_sub.end_date, "%Y-%m-%d").date()
                start_date = (curr_end + timedelta(days=1)) if curr_end >= today else today
            except Exception:
                start_date = today
        else:
            start_date = today

        end_date = start_date + timedelta(days=plan_info["days"])
        sessions = plan_info.get("sessions", 12)
        next_id = max([ms.membership_id for ms in self.memberships], default=0) + 1

        membership = Membership(
            membership_id=next_id,
            member_id=int(member_id),
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            cost=cost,
            total_sessions=sessions,
            remaining_sessions=sessions
        )

        member.membership_type = plan_name
        self.memberships.append(membership)
        self.record_payment(int(member_id), cost, method=payment_method, ref="Plan Renewal")
        self.save()
        return membership

    def freeze_member_membership(self, member_id: int) -> None:
        sub = self.get_active_membership(member_id)
        if not sub:
            raise ValueError(f"No active membership available for Member #{member_id} to freeze.")
        sub.freeze()
        self.save()

    def unfreeze_member_membership(self, member_id: int) -> None:
        sub = next((ms for ms in self.memberships if int(ms.member_id) == int(member_id) and getattr(ms, "is_frozen", False)), None)
        if not sub:
            raise ValueError(f"No frozen membership found for Member #{member_id}.")
        sub.unfreeze()
        self.save()

    def record_attendance(self, person_id: int) -> Attendance:
        member = self.find_member_by_id(person_id)
        trainer = self.find_trainer_by_id(person_id)

        if not member and not trainer:
            raise ValueError(f"Access Denied: ID #{person_id} does not exist in members or coaching staff.")

        today_str = datetime.now().strftime("%Y-%m-%d")

        for a in self.attendances:
            if int(a.member_id) == int(person_id) and a.timestamp.startswith(today_str):
                name = member.name if member else trainer.name
                raise ValueError(f"Duplicate Check-in: '{name}' has already checked in today ({today_str})!")

        if member:
            sub = self.get_active_membership(person_id)
            if not sub:
                raise ValueError(f"Access Denied: Member '{member.name}' subscription is Expired or Frozen.")
            sub.deduct_session()

        next_id = max([a.attendance_id for a in self.attendances], default=0) + 1
        attendance = Attendance(next_id, int(person_id))
        self.attendances.append(attendance)
        self.save()
        return attendance

    def record_attendance_by_token(self, token: str) -> Attendance:
        member = self.find_member_by_token(token)
        trainer = self.find_trainer_by_token(token)
        if member:
            return self.record_attendance(member.person_id)
        elif trainer:
            return self.record_attendance(trainer.person_id)
        raise ValueError("Unrecognized QR Pass: Token is invalid.")

    def delete_attendance(self, attendance_id: int) -> Attendance:
        target = next((a for a in self.attendances if a.attendance_id == attendance_id), None)
        if not target:
            raise ValueError(f"Attendance record #{attendance_id} does not exist.")
        self.attendances = [a for a in self.attendances if a.attendance_id != attendance_id]
        self.save()
        return target

    def get_currently_in_gym(self) -> List[Dict[str, Any]]:
        now = datetime.now()
        two_hours_ago = now - timedelta(hours=2)
        active_now = []

        for a in self.attendances:
            try:
                t = datetime.strptime(a.timestamp, "%Y-%m-%d %H:%M:%S")
                if two_hours_ago <= t <= now:
                    m = self.find_member_by_id(a.member_id)
                    tr = self.find_trainer_by_id(a.member_id)
                    role = "Member" if m else ("Trainer" if tr else "Unknown")
                    name = m.name if m else (tr.name if tr else "Unknown")

                    active_now.append({
                        "attendance_id": a.attendance_id,
                        "person_id": a.member_id,
                        "name": name,
                        "role": role,
                        "check_in_time": a.timestamp,
                        "duration_minutes": int((now - t).total_seconds() / 60)
                    })
            except (ValueError, TypeError):
                continue
        return active_now

    def get_daily_attendance_report(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        date_str = target_date or datetime.now().strftime("%Y-%m-%d")
        daily_records = []

        for a in self.attendances:
            if a.timestamp.startswith(date_str):
                m = self.find_member_by_id(a.member_id)
                tr = self.find_trainer_by_id(a.member_id)
                daily_records.append({
                    "attendance_id": a.attendance_id,
                    "member_id": a.member_id,
                    "name": m.name if m else (tr.name if tr else "Unknown"),
                    "role": "Member" if m else ("Trainer" if tr else "Unknown"),
                    "time": a.timestamp.split(" ")[1] if " " in a.timestamp else a.timestamp
                })
        return daily_records

    def get_dashboard_stats(self) -> Dict[str, Any]:
        total_members = len(self.members)
        active_members = len(self.filter_members_by_status(active=True))
        expired_members = total_members - active_members
        total_revenue = sum(p.amount for p in self.payments)

        now = datetime.now()
        two_hours_ago = now - timedelta(hours=2)
        today_str = now.strftime("%Y-%m-%d")

        in_gym = self.get_currently_in_gym()
        in_gym_now = len(in_gym)
        trainers_in_gym_now = len([p for p in in_gym if p.get("role") == "Trainer"])
        members_in_gym_now = len([p for p in in_gym if p.get("role") == "Member"])

        today_att_members = set()
        for a in self.attendances:
            if a.timestamp.startswith(today_str):
                today_att_members.add(a.member_id)

        method_totals = {}
        for p in self.payments:
            m = p.method.title()
            method_totals[m] = method_totals.get(m, 0.0) + p.amount

        retention_rate = (active_members / total_members * 100) if total_members > 0 else 0.0

        return {
            "total_members": total_members,
            "active_members": active_members,
            "expired_members": expired_members,
            "in_gym_now": in_gym_now,
            "trainers_in_gym_now": trainers_in_gym_now,
            "members_in_gym_now": members_in_gym_now,
            "today_attendance": len(today_att_members),
            "total_trainers": len(self.trainers),
            "total_revenue": total_revenue,
            "total_attendances": len(self.attendances),
            "retention_rate": round(retention_rate, 1),
            "method_totals": method_totals
        }

    def get_member_complete_profile(self, member_id: int) -> Dict[str, Any]:
        member = self.find_member_by_id(member_id)
        if not member:
            raise ValueError(f"Member #{member_id} not found.")

        sub = self.get_latest_membership(member_id)
        tr = self.find_trainer_by_id(member.trainer_id) if member.trainer_id else None

        member_att = [a for a in self.attendances if int(a.member_id) == int(member_id)]
        last_checkin = member_att[-1].timestamp if member_att else "Never"

        last_payment = [p for p in self.payments if int(p.member_id) == int(member_id)]
        last_payment_date = last_payment[-1].date if last_payment else "No payments yet"

        st = getattr(sub, "status", "Active" if (sub and sub.is_active) else "Expired") if sub else "No Subscription"
        rem_sess = getattr(sub, "remaining_sessions", 0) if sub else 0
        tot_sess = getattr(sub, "total_sessions", 0) if sub else 0

        prog = member.get_progress_summary()
        history = getattr(member, "inbody_history", [])

        return {
            "id": member.person_id,
            "name": member.name,
            "phone": member.phone,
            "trainer_assigned": tr.name if tr else "None",
            "trainer_specialization": tr.specialization if tr else "N/A",
            "membership_plan": member.membership_type,
            "status": st,
            "remaining_sessions": rem_sess,
            "total_sessions": tot_sess,
            "subscription_start": sub.start_date if sub else "N/A",
            "renewal_deadline": sub.end_date if sub else "N/A",
            "last_paid_at": last_payment_date,
            "last_checkin": last_checkin,
            "total_attendance_days": len(member_att),
            "inbody_progress": prog,
            "inbody_history": history
        }

    def record_payment(self, member_id: int, amount: float, method: str = "Cash", ref: Optional[str] = None) -> Payment:
        if float(amount) <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        next_id = max([p.payment_id for p in self.payments], default=0) + 1
        payment = Payment(next_id, int(member_id), float(amount), method=method, reference_number=ref)
        self.payments.append(payment)
        self.save()
        return payment

    def update_payment(self, payment_id: int, amount: float, method: str, ref: Optional[str] = None) -> Payment:
        self.load()
        target = next((p for p in self.payments if int(p.payment_id) == int(payment_id)), None)
        if not target:
            raise ValueError(f"Payment receipt #{payment_id} not found.")
        if float(amount) <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        target.amount = float(amount)
        target.method = method.title()
        if ref is not None:
            target.reference_number = ref
        self.save()
        return target

    def delete_payment(self, payment_id: int) -> Payment:
        self.load()
        target = next((p for p in self.payments if int(p.payment_id) == int(payment_id)), None)
        if not target:
            raise ValueError(f"Payment receipt #{payment_id} not found.")
        self.payments = [p for p in self.payments if int(p.payment_id) != int(payment_id)]
        self.save()
        return target

    def get_active_membership(self, member_id: int) -> Optional[Membership]:
        for ms in self.memberships:
            if int(ms.member_id) == int(member_id):
                if hasattr(ms, "is_frozen") and ms.is_frozen:
                    continue
                if ms.is_active:
                    return ms
        return None

    def get_latest_membership(self, member_id: int) -> Optional[Membership]:
        subs = [ms for ms in self.memberships if int(ms.member_id) == int(member_id)]
        return subs[-1] if subs else None
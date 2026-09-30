import os
from flask import Flask, render_template, request, jsonify, send_file
from services.gym_service import Gym, MEMBERSHIP_PLANS, TRAINER_TAX_RATE
from models import Trainer
from services.qr_manager import QRManager

app = Flask(__name__, template_folder="templates")
gym = Gym()

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- 1. الداشبورد والصالة الحية ----------------
@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    stats = gym.get_dashboard_stats()
    # إضافة عدد الكباتن المتواجدين حالياً بالصالة
    in_gym = gym.get_currently_in_gym()
    trainers_now = len([p for p in in_gym if p.get("role") == "Trainer"])
    members_now = len([p for p in in_gym if p.get("role") == "Member"])
    stats["trainers_in_gym_now"] = trainers_now
    stats["members_in_gym_now"] = members_now
    return jsonify(stats)

# ---------------- 2. إدارة الأعضاء ----------------
@app.route("/api/members", methods=["GET"])
def list_members():
    data = []
    for m in gym.members:
        sub = gym.get_latest_membership(m.person_id)
        tr = gym.find_trainer_by_id(m.trainer_id) if m.trainer_id else None
        data.append({
            "id": m.person_id,
            "name": m.name,
            "phone": m.phone,
            "plan": m.membership_type,
            "trainer": tr.name if tr else "بدون مدرب",
            "trainer_id": m.trainer_id,
            "remaining_sessions": getattr(sub, "remaining_sessions", 0) if sub else 0,
            "status": getattr(sub, "status", "Active" if (sub and sub.is_active) else "Expired") if sub else "No Subscription",
            "is_frozen": getattr(sub, "is_frozen", False) if sub else False
        })
    return jsonify(data)

@app.route("/api/members", methods=["POST"])
def add_member():
    req = request.json or {}
    try:
        w = float(req["weight"]) if req.get("weight") else None
        h = float(req["height"]) if req.get("height") else None
        fat = float(req["fat"]) if req.get("fat") else None
        mus = float(req["muscle"]) if req.get("muscle") else None
        tid = int(req["trainer_id"]) if req.get("trainer_id") else None

        m = gym.register_member(
            name=req["name"],
            phone=req["phone"],
            plan_name=req["plan"],
            payment_method=req.get("payment_method", "Cash"),
            trainer_id=tid,
            weight=w, height=h, fat_percentage=fat, muscle_mass=mus
        )
        return jsonify({"success": True, "member_id": m.person_id, "name": m.name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/members/<int:member_id>/renew", methods=["POST"])
def renew_member_endpoint(member_id):
    req = request.json or {}
    try:
        plan = req.get("plan")
        pay_method = req.get("payment_method", "Cash")
        w = float(req["weight"]) if req.get("weight") else None
        h = float(req["height"]) if req.get("height") else None
        fat = float(req["fat"]) if req.get("fat") else None
        mus = float(req["muscle"]) if req.get("muscle") else None

        sub = gym.renew_membership(
            member_id=member_id,
            plan_name=plan,
            payment_method=pay_method,
            weight=w, height=h, fat_percentage=fat, muscle_mass=mus
        )
        return jsonify({"success": True, "end_date": sub.end_date, "remaining_sessions": getattr(sub, "remaining_sessions", 0)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/members/<int:member_id>/profile", methods=["GET"])
def get_member_profile(member_id):
    try:
        profile = gym.get_member_complete_profile(member_id)
        return jsonify(profile)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/members/<int:member_id>/qr", methods=["GET"])
def get_member_qr(member_id):
    member = gym.find_member_by_id(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    qr_path = QRManager.generate_qr(member.person_id, member.qr_token)
    return send_file(qr_path, mimetype='image/png')

@app.route("/api/members/<int:member_id>/freeze", methods=["POST"])
def freeze_member(member_id):
    try:
        gym.freeze_member_membership(member_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/members/<int:member_id>/unfreeze", methods=["POST"])
def unfreeze_member(member_id):
    try:
        gym.unfreeze_member_membership(member_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    try:
        gym.delete_member(member_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ---------------- 3. الكباتن والبروفايل الكامل والـ QR ----------------
@app.route("/api/trainers", methods=["GET"])
def list_trainers():
    trainers = []
    in_gym_ids = {p["person_id"] for p in gym.get_currently_in_gym() if p.get("role") == "Trainer"}
    for t in gym.trainers:
        cnt = len([m for m in gym.members if m.trainer_id == t.person_id])
        trainers.append({
            "id": t.person_id,
            "name": t.name,
            "specialty": t.specialization,
            "trainees_count": cnt,
            "is_present_now": t.person_id in in_gym_ids
        })
    return jsonify(trainers)

@app.route("/api/trainers", methods=["POST"])
def add_trainer_endpoint():
    req = request.json or {}
    try:
        tid = gym.generate_trainer_id()
        t = Trainer(
            person_id=tid,
            name=req["name"].strip(),
            phone=req["phone"].strip(),
            specialization=req["specialty"].strip(),
            salary=float(req["salary"])
        )
        gym.add_trainer(t)
        return jsonify({"success": True, "trainer_id": tid, "name": t.name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/trainers/<int:trainer_id>/profile", methods=["GET"])
def get_trainer_profile_endpoint(trainer_id):
    try:
        profile = gym.get_trainer_full_profile(trainer_id)
        return jsonify(profile)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/trainers/<int:trainer_id>/qr", methods=["GET"])
def get_trainer_qr(trainer_id):
    trainer = gym.find_trainer_by_id(trainer_id)
    if not trainer:
        return jsonify({"error": "Trainer not found"}), 404
    token = getattr(trainer, "qr_token", str(trainer.person_id))
    qr_path = QRManager.generate_qr(trainer.person_id, token)
    return send_file(qr_path, mimetype='image/png')

@app.route("/api/trainers/<int:trainer_id>/checkin", methods=["POST"])
def trainer_checkin(trainer_id):
    try:
        att = gym.record_attendance(trainer_id)
        t = gym.find_trainer_by_id(trainer_id)
        return jsonify({"success": True, "trainer_name": t.name, "timestamp": att.timestamp})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ---------------- 4. سجل الاشتراكات المفصل ----------------
@app.route("/api/memberships", methods=["GET"])
def list_memberships():
    data = []
    for ms in reversed(gym.memberships):
        m = gym.find_member_by_id(ms.member_id)
        data.append({
            "membership_id": ms.membership_id,
            "member_id": ms.member_id,
            "member_name": m.name if m else "Unknown",
            "member_phone": m.phone if m else "N/A",
            "plan_name": getattr(m, "membership_type", "Standard"),
            "start_date": ms.start_date,
            "end_date": ms.end_date,
            "cost": ms.cost,
            "total_sessions": getattr(ms, "total_sessions", 12),
            "remaining_sessions": getattr(ms, "remaining_sessions", 0),
            "status": getattr(ms, "status", "Active" if ms.is_active else "Expired")
        })
    return jsonify(data)

# ---------------- 5. الحضور (أعضاء + كباتن) ----------------
@app.route("/api/attendance/live", methods=["GET"])
def get_live_attendance():
    return jsonify(gym.get_currently_in_gym())

@app.route("/api/attendance/daily", methods=["GET"])
def get_daily_attendance():
    records = gym.get_daily_attendance_report()
    # تدعيم كل حركة باسم ورتبة الشخص (كابتن أو عضو)
    for r in records:
        pid = r["member_id"]
        m = gym.find_member_by_id(pid)
        tr = gym.find_trainer_by_id(pid)
        r["role"] = "Member" if m else ("Trainer" if tr else "Unknown")
        r["name"] = m.name if m else (tr.name if tr else "Unknown")
    return jsonify(records)

@app.route("/api/attendance/checkin", methods=["POST"])
def checkin():
    req = request.json or {}
    try:
        if "token" in req and req["token"]:
            token = str(req["token"]).strip()
            att = gym.record_attendance_by_token(token)
            m = gym.find_member_by_token(token)
            tr = gym.find_trainer_by_token(token)
            person = m or tr
            role = "Member" if m else "Trainer"
        elif "member_id" in req and req["member_id"]:
            pid = int(req["member_id"])
            att = gym.record_attendance(pid)
            m = gym.find_member_by_id(pid)
            tr = gym.find_trainer_by_id(pid)
            person = m or tr
            role = "Member" if m else "Trainer"
        else:
            return jsonify({"success": False, "error": "ID or QR code is required"}), 400

        sub = gym.get_active_membership(m.person_id) if m else None
        rem = getattr(sub, "remaining_sessions", 0) if sub else "Staff"

        return jsonify({
            "success": True,
            "name": person.name,
            "role": role,
            "timestamp": att.timestamp,
            "remaining_sessions": rem
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ---------------- 6. السجل المالي ----------------
@app.route("/api/payments", methods=["GET"])
def list_payments():
    res = []
    for p in reversed(gym.payments):
        m = gym.find_member_by_id(p.member_id)
        res.append({
            "id": p.payment_id,
            "member_id": p.member_id,
            "member_name": m.name if m else "Unknown",
            "amount": p.amount,
            "method": p.method,
            "ref": p.reference_number,
            "date": p.date
        })
    return jsonify(res)

@app.route("/api/payments", methods=["POST"])
def add_payment():
    req = request.json or {}
    try:
        mid = int(req["member_id"])
        amt = float(req["amount"])
        method = req.get("method", "Cash")
        ref = req.get("ref", "Manual Payment")

        if not gym.find_member_by_id(mid):
            return jsonify({"success": False, "error": f"Member #{mid} does not exist."}), 404

        p = gym.record_payment(mid, amt, method=method, ref=ref)
        return jsonify({"success": True, "payment_id": p.payment_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/payments/<int:payment_id>", methods=["PUT"])
def update_payment_endpoint(payment_id):
    req = request.json or {}
    try:
        amt = float(req["amount"])
        method = req.get("method", "Cash")
        ref = req.get("ref")
        gym.update_payment(payment_id, amt, method, ref)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/payments/<int:payment_id>", methods=["DELETE"])
def delete_payment_endpoint(payment_id):
    try:
        gym.delete_payment(payment_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/plans", methods=["GET"])
def get_plans():
    return jsonify({"plans": MEMBERSHIP_PLANS, "tax_rate": TRAINER_TAX_RATE})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
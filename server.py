import os
from flask import Flask, render_template, request, jsonify
from services.gym_service import Gym, MEMBERSHIP_PLANS, TRAINER_TAX_RATE

app = Flask(__name__, template_folder="templates")
gym = Gym()

# ---------------- الصفحة الرئيسية ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- 1. إحصائيات الداشبورد اللحظية ----------------
@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    stats = gym.get_dashboard_stats()
    return jsonify(stats)

# ---------------- 2. إدارة الأعضاء والـ InBody ----------------
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

@app.route("/api/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    req = request.json or {}
    try:
        name = req.get("name")
        phone = req.get("phone")
        plan = req.get("plan")
        trainer_id = req.get("trainer_id")

        member = gym.find_member_by_id(member_id)
        if not member:
            return jsonify({"error": "Member not found"}), 404

        gym.update_member(member_id, name or member.name, phone or member.phone, plan or member.membership_type)
        if trainer_id is not None:
            member.trainer_id = int(trainer_id) if trainer_id else None
            gym.save()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/members/<int:member_id>/profile", methods=["GET"])
def get_member_profile(member_id):
    try:
        profile = gym.get_member_complete_profile(member_id)
        return jsonify(profile)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

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

# ---------------- 3. متابعة الكباتن والنتائج ----------------
@app.route("/api/trainers", methods=["GET"])
def list_trainers():
    trainers = []
    for t in gym.trainers:
        cnt = len([m for m in gym.members if m.trainer_id == t.person_id])
        trainers.append({
            "id": t.person_id,
            "name": t.name,
            "phone": t.phone,
            "specialty": t.specialization,
            "salary": t.salary,
            "trainees_count": cnt
        })
    return jsonify(trainers)

@app.route("/api/trainers/<int:trainer_id>/trainees", methods=["GET"])
def get_trainer_trainees(trainer_id):
    try:
        report = gym.get_trainer_trainees_report(trainer_id)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

# ---------------- 4. الحضور والصالة الحية (بالكاميرا أو الكود اليدوي) ----------------
@app.route("/api/attendance/live", methods=["GET"])
def get_live_attendance():
    return jsonify(gym.get_currently_in_gym())

@app.route("/api/attendance/daily", methods=["GET"])
def get_daily_attendance():
    return jsonify(gym.get_daily_attendance_report())

@app.route("/api/attendance/checkin", methods=["POST"])
def checkin():
    req = request.json or {}
    try:
        # فحص إذا كان التسجيل عن طريق مسح كاميرا QR أو كتابة Member ID
        if "token" in req and req["token"]:
            token = str(req["token"]).strip()
            att = gym.record_attendance_by_token(token)
            m = gym.find_member_by_token(token)
        elif "member_id" in req and req["member_id"]:
            mid = int(req["member_id"])
            att = gym.record_attendance(mid)
            m = gym.find_member_by_id(mid)
        else:
            return jsonify({"success": False, "error": "Member ID or QR code is required"}), 400

        if not m:
            return jsonify({"success": False, "error": "Member not found"}), 404

        sub = gym.get_active_membership(m.person_id)
        rem = getattr(sub, "remaining_sessions", 0) if sub else 0
        return jsonify({
            "success": True,
            "member_name": m.name,
            "timestamp": att.timestamp,
            "remaining_sessions": rem
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ---------------- 5. السجل المالي (عرض، تسجيل، تعديل، حذف) ----------------
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
def update_payment(payment_id):
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
def delete_payment(payment_id):
    try:
        gym.delete_payment(payment_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ---------------- 6. الباقات والضرائب ----------------
@app.route("/api/plans", methods=["GET"])
def get_plans():
    return jsonify({"plans": MEMBERSHIP_PLANS, "tax_rate": TRAINER_TAX_RATE})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
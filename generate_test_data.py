"""
FitZone Pro - Dynamic Test Data Generator
Generates data/data.json with dates relative to TODAY.
Run: python generate_test_data.py
"""
import json
import os
from datetime import datetime, timedelta


def d(days_ago=0, h=0, m=0):
    """Return date string N days ago (with optional hours/minutes offset)."""
    dt = datetime.now() - timedelta(days=days_ago, hours=h, minutes=m)
    return dt.strftime("%Y-%m-%d")


def ts(days_ago=0, h=0, m=0):
    """Return timestamp string N days ago."""
    dt = datetime.now() - timedelta(days=days_ago, hours=h, minutes=m)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ================================================================
# Helper: build an InBody history for a member
# ================================================================
def inbody_series(start_days_ago, records):
    """
    records: list of (days_ago, weight, height, fat, muscle, notes)
    """
    return [
        {
            "date": d(days_ago),
            "weight": w,
            "height": h,
            "fat_percentage": f,
            "muscle_mass": m,
            "notes": notes,
        }
        for (days_ago, w, h, f, m, notes) in records
    ]


# ================================================================
# Build the dataset
# ================================================================
YEAR = 365
HALF_YEAR = 182
THREE_MONTHS = 90
MONTH = 30

data = {
    "members": [
        # ---------------------------------------------------------
        # 1. Ahmed Hassan - 1 year with Hossam - massive fat loss
        # ---------------------------------------------------------
        {
            "person_id": 10001,
            "name": "Ahmed Hassan",
            "phone": "01012345678",
            "membership_type": "Annual VIP (All Access - 365 Days)",
            "join_date": d(YEAR),
            "trainer_id": 20001,
            "qr_token": "qr_ahmed_hassan_001",
            "inbody_history": inbody_series(YEAR, [
                (YEAR,  95.0, 180.0, 32.0, 32.0, "Initial - obese"),
                (300,   92.0, 180.0, 30.0, 33.0, "Month 2 - starting cardio"),
                (240,   88.0, 180.0, 26.5, 35.0, "Month 4 - visible progress"),
                (180,   84.0, 180.0, 22.0, 37.5, "Month 6 - strength up"),
                (120,   80.0, 180.0, 17.0, 40.0, "Month 8 - fit body"),
                (60,    76.5, 180.0, 12.0, 43.0, "Month 10 - shredded"),
                (5,     75.0, 180.0, 10.5, 44.0, "1-year - incredible"),
            ]),
        },

        # ---------------------------------------------------------
        # 2. Sara Mohamed - 10 months with Mona - cardio queen
        # ---------------------------------------------------------
        {
            "person_id": 10002,
            "name": "Sara Mohamed",
            "phone": "01023456789",
            "membership_type": "Annual VIP (All Access - 365 Days)",
            "join_date": d(300),
            "trainer_id": 20002,
            "qr_token": "qr_sara_mohamed_002",
            "inbody_history": inbody_series(300, [
                (300,  78.0, 165.0, 38.0, 22.0, "Initial - post-pregnancy"),
                (240,  74.0, 165.0, 34.0, 23.0, "Month 2 - cardio focus"),
                (150,  68.0, 165.0, 28.0, 25.0, "Month 5 - great progress"),
                (60,   62.0, 165.0, 22.0, 27.0, "Month 8 - toned"),
                (5,    58.0, 165.0, 18.5, 28.0, "Month 10 - athletic"),
            ]),
        },

        # ---------------------------------------------------------
        # 3. Omar Ali - 1 year with Karim - bulked up
        # ---------------------------------------------------------
        {
            "person_id": 10003,
            "name": "Omar Ali",
            "phone": "01034567890",
            "membership_type": "Annual VIP (All Access - 365 Days)",
            "join_date": d(YEAR),
            "trainer_id": 20003,
            "qr_token": "qr_omar_ali_003",
            "inbody_history": inbody_series(YEAR, [
                (YEAR,  68.0, 175.0, 18.0, 30.0, "Initial - skinny"),
                (270,   72.0, 175.0, 16.0, 34.0, "Month 3 - gaining mass"),
                (180,   76.0, 175.0, 14.0, 38.0, "Month 6 - muscular"),
                (90,    79.0, 175.0, 12.0, 41.0, "Month 9 - strong"),
                (5,     81.0, 175.0, 10.5, 43.0, "1-year - bodybuilder"),
            ]),
        },

        # ---------------------------------------------------------
        # 4. Nour Ibrahim - 6 months with Hossam - transformed
        # ---------------------------------------------------------
        {
            "person_id": 10004,
            "name": "Nour Ibrahim",
            "phone": "01045678901",
            "membership_type": "Fitness + Cardio (Full Month - 30 Days)",
            "join_date": d(180),
            "trainer_id": 20001,
            "qr_token": "qr_nour_ibrahim_004",
            "inbody_history": inbody_series(180, [
                (180,  85.0, 170.0, 35.0, 25.0, "Initial - overweight"),
                (120,  81.0, 170.0, 31.0, 26.5, "Month 2"),
                (60,   76.0, 170.0, 26.0, 28.0, "Month 4"),
                (5,    72.0, 170.0, 21.0, 29.5, "Month 6 - transformed"),
            ]),
        },

        # ---------------------------------------------------------
        # 5. Youssef Khaled - 1 year with Hossam - biggest loss
        # ---------------------------------------------------------
        {
            "person_id": 10005,
            "name": "Youssef Khaled",
            "phone": "01056789012",
            "membership_type": "Annual VIP (All Access - 365 Days)",
            "join_date": d(YEAR),
            "trainer_id": 20001,
            "qr_token": "qr_youssef_khaled_005",
            "inbody_history": inbody_series(YEAR, [
                (YEAR,  115.0, 185.0, 40.0, 35.0, "Initial - severely obese"),
                (270,   105.0, 185.0, 35.0, 37.0, "Month 3 - 10kg lost"),
                (180,   96.0, 185.0, 30.0, 39.0, "Month 6 - huge change"),
                (90,    89.0, 185.0, 24.0, 42.0, "Month 9 - athletic"),
                (5,     84.0, 185.0, 18.0, 45.0, "1-year - 31kg down!"),
            ]),
        },

        # ---------------------------------------------------------
        # 6. Layla Ahmed - 1 year with Mona - lean
        # ---------------------------------------------------------
        {
            "person_id": 10006,
            "name": "Layla Ahmed",
            "phone": "01067890123",
            "membership_type": "Annual VIP (All Access - 365 Days)",
            "join_date": d(YEAR),
            "trainer_id": 20002,
            "qr_token": "qr_layla_ahmed_006",
            "inbody_history": inbody_series(YEAR, [
                (YEAR,  82.0, 162.0, 40.0, 20.0, "Initial - overweight"),
                (270,   75.0, 162.0, 34.0, 21.5, "Month 3"),
                (180,   68.0, 162.0, 27.0, 23.0, "Month 6"),
                (90,    62.0, 162.0, 21.0, 25.0, "Month 9"),
                (5,     57.0, 162.0, 16.0, 26.5, "1-year - lean"),
            ]),
        },

        # ---------------------------------------------------------
        # 7. Karim Adel - 1 year with Karim - gained 17kg muscle
        # ---------------------------------------------------------
        {
            "person_id": 10007,
            "name": "Karim Adel",
            "phone": "01078901234",
            "membership_type": "Annual VIP (All Access - 365 Days)",
            "join_date": d(YEAR),
            "trainer_id": 20003,
            "qr_token": "qr_karim_adel_007",
            "inbody_history": inbody_series(YEAR, [
                (YEAR,  60.0, 178.0, 15.0, 28.0, "Initial - very skinny"),
                (270,   66.0, 178.0, 13.0, 33.0, "Month 3"),
                (180,   72.0, 178.0, 11.0, 38.0, "Month 6"),
                (90,    76.0, 178.0, 10.0, 42.0, "Month 9"),
                (5,     79.0, 178.0,  8.5, 45.5, "1-year - +17.5kg muscle"),
            ]),
        },

        # ---------------------------------------------------------
        # 8. Hana Mostafa - new member (with Mona) - only 1 InBody
        # ---------------------------------------------------------
        {
            "person_id": 10008,
            "name": "Hana Mostafa",
            "phone": "01089012345",
            "membership_type": "Fitness (Full Month - 30 Days)",
            "join_date": d(15),
            "trainer_id": 20002,
            "qr_token": "qr_hana_mostafa_008",
            "inbody_history": inbody_series(15, [
                (15, 68.0, 167.0, 30.0, 23.0, "Initial - new member"),
            ]),
        },

        # ---------------------------------------------------------
        # 9. Tamer Samy - 3 months, no trainer, near end
        # ---------------------------------------------------------
        {
            "person_id": 10009,
            "name": "Tamer Samy",
            "phone": "01090123456",
            "membership_type": "Fitness (Half Month - 15 Days)",
            "join_date": d(10),
            "trainer_id": None,
            "qr_token": "qr_tamer_samy_009",
            "inbody_history": inbody_series(10, [
                (10, 90.0, 175.0, 33.0, 28.0, "Initial"),
            ]),
        },

        # ---------------------------------------------------------
        # 10. Rana Fouad - expired member (no renewal)
        # ---------------------------------------------------------
        {
            "person_id": 10010,
            "name": "Rana Fouad",
            "phone": "01001234567",
            "membership_type": "Fitness (Full Month - 30 Days)",
            "join_date": d(120),
            "trainer_id": None,
            "qr_token": "qr_rana_fouad_010",
            "inbody_history": inbody_series(120, [
                (120, 74.0, 168.0, 32.0, 22.0, "Initial"),
            ]),
        },
    ],

    "trainers": [
        {
            "person_id": 20001,
            "name": "Hossam Adel",
            "phone": "01111111111",
            "specialization": "Iron / Bodybuilding",
            "salary": 8000.0,
            "qr_token": "qr_coach_hossam_001",
        },
        {
            "person_id": 20002,
            "name": "Mona Samir",
            "phone": "01122222222",
            "specialization": "Cardio",
            "salary": 7000.0,
            "qr_token": "qr_coach_mona_002",
        },
        {
            "person_id": 20003,
            "name": "Karim Fathy",
            "phone": "01133333333",
            "specialization": "Crossfit",
            "salary": 7500.0,
            "qr_token": "qr_coach_karim_003",
        },
    ],

    "memberships": [
        # Ahmed - Annual VIP - still active
        {
            "membership_id": 1, "member_id": 10001,
            "start_date": d(YEAR), "end_date": d(-30),
            "cost": 5450.0, "total_sessions": 300, "remaining_sessions": 15,
            "is_frozen": False, "freeze_date": None,
            "status": "Active", "is_active": True,
        },
        # Sara - Annual VIP - active
        {
            "membership_id": 2, "member_id": 10002,
            "start_date": d(300), "end_date": d(-65),
            "cost": 5450.0, "total_sessions": 300, "remaining_sessions": 80,
            "is_frozen": False, "freeze_date": None,
            "status": "Active", "is_active": True,
        },
        # Omar - Annual VIP - EXPIRED
        {
            "membership_id": 3, "member_id": 10003,
            "start_date": d(YEAR), "end_date": d(30),
            "cost": 5450.0, "total_sessions": 300, "remaining_sessions": 25,
            "is_frozen": False, "freeze_date": None,
            "status": "Expired", "is_active": False,
        },
        # Nour - Monthly - active
        {
            "membership_id": 4, "member_id": 10004,
            "start_date": d(15), "end_date": d(-15),
            "cost": 990.0, "total_sessions": 26, "remaining_sessions": 20,
            "is_frozen": False, "freeze_date": None,
            "status": "Active", "is_active": True,
        },
        # Youssef - Annual VIP - EXPIRED
        {
            "membership_id": 5, "member_id": 10005,
            "start_date": d(YEAR), "end_date": d(20),
            "cost": 5450.0, "total_sessions": 300, "remaining_sessions": 42,
            "is_frozen": False, "freeze_date": None,
            "status": "Expired", "is_active": False,
        },
        # Layla - Annual VIP - EXPIRED
        {
            "membership_id": 6, "member_id": 10006,
            "start_date": d(YEAR), "end_date": d(60),
            "cost": 4950.0, "total_sessions": 300, "remaining_sessions": 35,
            "is_frozen": False, "freeze_date": None,
            "status": "Expired", "is_active": False,
        },
        # Karim Adel - Annual VIP - EXPIRED
        {
            "membership_id": 7, "member_id": 10007,
            "start_date": d(YEAR), "end_date": d(45),
            "cost": 5450.0, "total_sessions": 300, "remaining_sessions": 10,
            "is_frozen": False, "freeze_date": None,
            "status": "Expired", "is_active": False,
        },
        # Hana - Monthly - active
        {
            "membership_id": 8, "member_id": 10008,
            "start_date": d(15), "end_date": d(-15),
            "cost": 770.0, "total_sessions": 24, "remaining_sessions": 22,
            "is_frozen": False, "freeze_date": None,
            "status": "Active", "is_active": True,
        },
        # Tamer - Half month - about to expire
        {
            "membership_id": 9, "member_id": 10009,
            "start_date": d(10), "end_date": d(-5),
            "cost": 350.0, "total_sessions": 12, "remaining_sessions": 3,
            "is_frozen": False, "freeze_date": None,
            "status": "Active", "is_active": True,
        },
        # Rana - EXPIRED
        {
            "membership_id": 10, "member_id": 10010,
            "start_date": d(120), "end_date": d(90),
            "cost": 600.0, "total_sessions": 24, "remaining_sessions": 0,
            "is_frozen": False, "freeze_date": None,
            "status": "Expired", "is_active": False,
        },
    ],

    "payments": [
        {"payment_id": 1, "member_id": 10001, "amount": 5450.0, "method": "Cash",
         "reference_number": "Annual VIP + Trainer", "date": ts(YEAR)},
        {"payment_id": 2, "member_id": 10002, "amount": 5450.0, "method": "Visa",
         "reference_number": "Annual VIP + Trainer", "date": ts(300)},
        {"payment_id": 3, "member_id": 10003, "amount": 5450.0, "method": "Instapay",
         "reference_number": "Annual VIP + Trainer", "date": ts(YEAR)},
        {"payment_id": 4, "member_id": 10004, "amount": 990.0, "method": "Cash",
         "reference_number": "Plan + Trainer", "date": ts(15)},
        {"payment_id": 5, "member_id": 10005, "amount": 5450.0, "method": "Vodafone Cash",
         "reference_number": "Annual VIP + Trainer", "date": ts(YEAR)},
        {"payment_id": 6, "member_id": 10006, "amount": 4950.0, "method": "Cash",
         "reference_number": "Annual VIP", "date": ts(YEAR)},
        {"payment_id": 7, "member_id": 10007, "amount": 5450.0, "method": "Visa",
         "reference_number": "Annual VIP + Trainer", "date": ts(YEAR)},
        {"payment_id": 8, "member_id": 10008, "amount": 770.0, "method": "Cash",
         "reference_number": "Plan + Trainer", "date": ts(15)},
        {"payment_id": 9, "member_id": 10009, "amount": 350.0, "method": "Cash",
         "reference_number": "Enrollment", "date": ts(10)},
        {"payment_id": 10, "member_id": 10010, "amount": 600.0, "method": "Cash",
         "reference_number": "Enrollment", "date": ts(120)},
        {"payment_id": 11, "member_id": 10001, "amount": 500.0, "method": "Cash",
         "reference_number": "Personal Training Sessions", "date": ts(30)},
        {"payment_id": 12, "member_id": 10005, "amount": 1500.0, "method": "Visa",
         "reference_number": "Supplements + Nutrition", "date": ts(60)},
    ],

    "attendances": [
        # Historical visits
        {"attendance_id": 1, "member_id": 10001, "timestamp": ts(15)},
        {"attendance_id": 2, "member_id": 10001, "timestamp": ts(13)},
        {"attendance_id": 3, "member_id": 10001, "timestamp": ts(10)},
        {"attendance_id": 4, "member_id": 10001, "timestamp": ts(7)},
        {"attendance_id": 5, "member_id": 10001, "timestamp": ts(5)},
        {"attendance_id": 6, "member_id": 10001, "timestamp": ts(3)},
        {"attendance_id": 7, "member_id": 10001, "timestamp": ts(1)},

        {"attendance_id": 8, "member_id": 10002, "timestamp": ts(5)},
        {"attendance_id": 9, "member_id": 10002, "timestamp": ts(3)},
        {"attendance_id": 10, "member_id": 10002, "timestamp": ts(1)},

        {"attendance_id": 11, "member_id": 10004, "timestamp": ts(10)},
        {"attendance_id": 12, "member_id": 10004, "timestamp": ts(6)},
        {"attendance_id": 13, "member_id": 10004, "timestamp": ts(3)},

        {"attendance_id": 14, "member_id": 10008, "timestamp": ts(12)},
        {"attendance_id": 15, "member_id": 10008, "timestamp": ts(8)},
        {"attendance_id": 16, "member_id": 10008, "timestamp": ts(4)},

        {"attendance_id": 17, "member_id": 10009, "timestamp": ts(9)},
        {"attendance_id": 18, "member_id": 10009, "timestamp": ts(7)},
        {"attendance_id": 19, "member_id": 10009, "timestamp": ts(5)},
        {"attendance_id": 20, "member_id": 10009, "timestamp": ts(2)},

        # Currently in gym (last 2 hours) - these show on the LIVE dashboard
        {"attendance_id": 21, "member_id": 20001, "timestamp": ts(0, h=1, m=30)},   # Coach Hossam
        {"attendance_id": 22, "member_id": 20002, "timestamp": ts(0, h=1, m=15)},   # Coach Mona
        {"attendance_id": 23, "member_id": 10001, "timestamp": ts(0, h=1, m=0)},    # Ahmed
        {"attendance_id": 24, "member_id": 10002, "timestamp": ts(0, h=0, m=45)},   # Sara
        {"attendance_id": 25, "member_id": 10004, "timestamp": ts(0, h=0, m=30)},   # Nour
        {"attendance_id": 26, "member_id": 10008, "timestamp": ts(0, h=0, m=15)},   # Hana
    ],

    "body_metrics": [],
}


# ================================================================
# Write to file
# ================================================================
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "data.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Generated: {output_path}")
print(f"Members:    {len(data['members'])}")
print(f"Trainers:   {len(data['trainers'])}")
print(f"Memberships:{len(data['memberships'])}")
print(f"Payments:   {len(data['payments'])}")
print(f"Attendances:{len(data['attendances'])}")
print(f"Reference date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
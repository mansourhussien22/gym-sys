import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
from datetime import datetime
from services import Gym, MEMBERSHIP_PLANS, QRManager
from models import Member, Trainer, Payment

try:
    from services import TRAINER_TAX_RATE
except ImportError:
    TRAINER_TAX_RATE = 0.10

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GymApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FitZone Pro — Gym Management Platform")
        self.geometry("1240x760")
        self.minsize(1050, 680)

        # تحميل خدمة الجيم مباشرة في الذاكرة لسرعة الأداء
        self.gym = Gym()
        self._search_job = None

        # تشغيل شاشة تسجيل الدخول أولاً داخل نفس النافذة بدون أي بطء
        self._show_login_screen()

    # =============================================================
    # شاشة تسجيل الدخول السريعة (بدون نصوص افتراضية)
    # =============================================================
    def _show_login_screen(self):
        self._clear_window()
        self.configure(fg_color="#090d16")

        # الصندوق المركزي لتسجيل الدخول
        self.login_box = ctk.CTkFrame(self, width=420, height=440, corner_radius=15, fg_color="#111827", border_width=1, border_color="#1f2937")
        self.login_box.place(relx=0.5, rely=0.5, anchor="center")
        self.login_box.pack_propagate(False)

        ctk.CTkLabel(self.login_box, text="⚡ FitZone Pro", font=ctk.CTkFont(size=26, weight="bold"), text_color="#3b82f6").pack(pady=(45, 5))
        ctk.CTkLabel(self.login_box, text="Administrative Sign In", font=ctk.CTkFont(size=13), text_color="#9ca3af").pack(pady=(0, 25))

        # الخانات فارغة تماماً كما طلبت
        self.e_user = ctk.CTkEntry(self.login_box, placeholder_text="Username", width=300, height=42, fg_color="#1f2937", border_color="#374151")
        self.e_user.pack(pady=10)

        self.e_pass = ctk.CTkEntry(self.login_box, placeholder_text="Password", width=300, height=42, fg_color="#1f2937", border_color="#374151", show="*")
        self.e_pass.pack(pady=10)

        # دعم زر Enter لتسجيل الدخول الفوري
        self.e_user.bind("<Return>", lambda e: self.e_pass.focus())
        self.e_pass.bind("<Return>", lambda e: self._verify_login())

        ctk.CTkButton(
            self.login_box, text="Sign In", width=300, height=44, fg_color="#2563eb", hover_color="#1d4ed8",
            font=ctk.CTkFont(size=14, weight="bold"), command=self._verify_login
        ).pack(pady=(25, 10))

        self.e_user.focus()

    def _verify_login(self):
        u = self.e_user.get().strip()
        p = self.e_pass.get().strip()
        if u == "admin" and p == "admin":
            self.login_box.destroy()
            self._setup_main_layout()
        else:
            messagebox.showerror("Access Denied", "Invalid username or password!\nPlease enter valid credentials.")

    # =============================================================
    # إعداد الواجهة الرئيسية (سلسة وسريعة)
    # =============================================================
    def _setup_main_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_container()
        self.show_dashboard()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#111827")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        brand_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_box.pack(padx=20, pady=(25, 20), anchor="w")

        ctk.CTkLabel(brand_box, text="⚡ FitZone Pro", font=ctk.CTkFont(size=20, weight="bold"), text_color="#3b82f6").pack()

        # عناصر السايدبار النظيفة والصريحة
        self._make_menu_btn("📊 Dashboard", self.show_dashboard)
        self._make_menu_btn("👥 Members", self.show_members)
        self._make_menu_btn("🏋 Trainers", self.show_trainers)
        self._make_menu_btn("📑 Memberships", self.show_memberships)
        self._make_menu_btn("⏱ Attendance", self.show_attendance)
        self._make_menu_btn("💳 Financial Ledger", self.show_payments)

        # زر الخروج السريع النظيف
        exit_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Exit",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            height=42,
            fg_color="#7f1d1d",
            text_color="#fca5a5",
            hover_color="#991b1b",
            command=self._exit_app
        )
        exit_btn.pack(side="bottom", padx=15, pady=20, fill="x")

    def _exit_app(self):
        self.quit()
        self.destroy()

    def _make_menu_btn(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            height=40,
            fg_color="transparent",
            text_color="#9ca3af",
            hover_color="#1f2937",
            command=command
        )
        btn.pack(padx=15, pady=4, fill="x")
        return btn

    def _build_main_container(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#090d16")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def _clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    # =============================================================
    # 1. Dashboard
    # =============================================================
    def show_dashboard(self):
        self._clear_main()
        stats = self.gym.get_dashboard_stats()

        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(header, text="Operations & Financial Overview", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text=f"Retention Rate: {stats.get('retention_rate', 0)}%", text_color="#2dd4bf", font=ctk.CTkFont(size=14, weight="bold")).pack(side="right")

        cards = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards.pack(fill="x", padx=25, pady=5)
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_card(cards, 0, 0, "Currently in Gym", str(stats.get("in_gym_now", 0)), "Last 2 hours presence", "#f59e0b")
        self._create_card(cards, 0, 1, "Today's Attendance", str(stats.get("today_attendance", 0)), "Unique entries today", "#3b82f6")
        self._create_card(cards, 0, 2, "Active Members", str(stats.get("active_members", 0)), "Access authorized", "#10b981")
        self._create_card(cards, 0, 3, "Total Revenue", f"${stats.get('total_revenue', 0):,.2f}", "Total income collected", "#8b5cf6")

        cards_2 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_2.pack(fill="x", padx=25, pady=(15, 5))
        cards_2.grid_columnconfigure((0, 1, 2), weight=1)

        self._create_card(cards_2, 0, 0, "Expired / Frozen", str(stats.get("expired_members", 0)), "Requires action", "#ef4444")
        self._create_card(cards_2, 0, 1, "Total Registered", str(stats.get("total_members", 0)), "Full records count", "#6b7280")
        self._create_card(cards_2, 0, 2, "Coaching Staff", str(stats.get("total_trainers", 0)), "Active coaches", "#06b6d4")

    def _create_card(self, parent, row, col, title, val, sub, color):
        card = ctk.CTkFrame(parent, fg_color="#1f2937", corner_radius=10, height=105)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        card.pack_propagate(False)

        top_line = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0)
        top_line.pack(side="top", fill="x")

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=22, weight="bold"), text_color="white").pack(anchor="w", padx=15, pady=(2, 0))
        ctk.CTkLabel(card, text=sub, font=ctk.CTkFont(size=11), text_color="#6b7280").pack(anchor="w", padx=15, pady=(2, 5))

    # =============================================================
    # 2. Members (بحث لحظي فائق السرعة + تعديل وحذف وتجميد)
    # =============================================================
    def show_members(self):
        self._clear_main()

        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(top_bar, text="Members Management", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkButton(top_bar, text="+ Register Member", fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(weight="bold"), command=self._popup_add_member).pack(side="right")

        filter_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filter_bar.pack(fill="x", padx=25, pady=(0, 15))

        self.m_search = ctk.CTkEntry(filter_bar, placeholder_text="Type name, phone, or ID (Live Search)...", width=340, fg_color="#111827")
        self.m_search.pack(side="left", padx=(0, 10))
        
        # Debounced Search: سرعة فائقة تمنع التهنيج أثناء الكتابة
        self.m_search.bind("<KeyRelease>", self._debounce_search)

        self.filter_var = ctk.StringVar(value="All Members")
        filter_menu = ctk.CTkOptionMenu(filter_bar, values=["All Members", "Active Only", "Expired Only", "Frozen Only"], variable=self.filter_var, command=self._apply_member_filter)
        filter_menu.pack(side="right")

        self.members_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="#111827")
        self.members_scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        self._render_members_list(self.gym.members)

    def _debounce_search(self, event=None):
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(150, self._apply_member_search)

    def _render_members_list(self, members_list):
        for w in self.members_scroll.winfo_children():
            w.destroy()

        if not members_list:
            ctk.CTkLabel(self.members_scroll, text="No matching members found.", text_color="gray").pack(pady=40)
            return

        for m in members_list:
            sub = self.gym.get_latest_membership(m.person_id)
            status = getattr(sub, "status", "Active" if (sub and sub.is_active) else "Expired") if sub else "No Subscription"
            remaining = getattr(sub, "remaining_sessions", 0) if sub else 0
            is_frozen = getattr(sub, "is_frozen", False) if sub else False

            row = ctk.CTkFrame(self.members_scroll, fg_color="#1f2937", corner_radius=8)
            row.pack(fill="x", pady=4, padx=5)

            ctk.CTkButton(row, text="Delete", width=55, fg_color="#dc2626", hover_color="#b91c1c", command=lambda mid=m.person_id: self._delete_member(mid)).pack(side="right", padx=(2, 8), pady=8)
            ctk.CTkButton(row, text="Edit", width=55, fg_color="#2563eb", hover_color="#1d4ed8", command=lambda mem=m: self._popup_edit_member(mem)).pack(side="right", padx=2, pady=8)
            ctk.CTkButton(row, text="Profile", width=65, fg_color="#4338ca", hover_color="#3730a3", command=lambda mid=m.person_id: self._show_member_full_profile(mid)).pack(side="right", padx=2, pady=8)

            if is_frozen:
                ctk.CTkButton(row, text="Unfreeze", width=70, fg_color="#059669", hover_color="#047857", command=lambda mid=m.person_id: self._action_unfreeze(mid)).pack(side="right", padx=2, pady=8)
            else:
                ctk.CTkButton(row, text="Freeze", width=60, fg_color="#d97706", hover_color="#b45309", command=lambda mid=m.person_id: self._action_freeze(mid)).pack(side="right", padx=2, pady=8)

            ctk.CTkButton(row, text="Renew", width=55, fg_color="#10b981", hover_color="#059669", command=lambda mem=m: self._popup_renew_member_flow(mem.person_id)).pack(side="right", padx=2, pady=8)
            ctk.CTkButton(row, text="QR", width=45, fg_color="#374151", hover_color="#4b5563", command=lambda mem=m: self._show_qr_popup(mem)).pack(side="right", padx=2, pady=8)

            s_color = "#10b981" if status == "Active" else ("#f59e0b" if status == "Frozen" else "#ef4444")
            ctk.CTkLabel(row, text=status.upper(), fg_color=s_color, text_color="white", corner_radius=6, width=65, font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", padx=6, pady=8)
            ctk.CTkLabel(row, text=f"{remaining} S", fg_color="#111827", text_color="#38bdf8", corner_radius=6, width=50, font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", padx=2, pady=8)

            tr = self.gym.find_trainer_by_id(m.trainer_id) if m.trainer_id else None
            tr_text = f"Coach: {tr.name}" if tr else "No Coach"
            info = f"#{m.person_id} | {m.name} | 📞 {m.phone} | {m.membership_type} | {tr_text}"
            ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=8)

    def _apply_member_search(self):
        q = self.m_search.get().strip().lower()
        if not q:
            self._render_members_list(self.gym.members)
            return
        matched = [m for m in self.gym.members if q in m.name.lower() or q in str(m.person_id) or q in m.phone]
        self._render_members_list(matched)

    def _apply_member_filter(self, choice):
        if choice == "Active Only":
            self._render_members_list([m for m in self.gym.members if getattr(self.gym.get_latest_membership(m.person_id), "status", "") == "Active"])
        elif choice == "Expired Only":
            self._render_members_list([m for m in self.gym.members if getattr(self.gym.get_latest_membership(m.person_id), "status", "") == "Expired"])
        elif choice == "Frozen Only":
            self._render_members_list([m for m in self.gym.members if getattr(self.gym.get_latest_membership(m.person_id), "status", "") == "Frozen"])
        else:
            self._render_members_list(self.gym.members)

    def _popup_edit_member(self, member: Member):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Edit Member #{member.person_id}")
        popup.geometry("420x400")
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Edit Member #{member.person_id}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        ctk.CTkLabel(popup, text="Full Name:", font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", padx=30)
        e_name = ctk.CTkEntry(popup)
        e_name.insert(0, member.name)
        e_name.pack(fill="x", padx=30, pady=(2, 8))

        ctk.CTkLabel(popup, text="Phone Number:", font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", padx=30)
        e_phone = ctk.CTkEntry(popup)
        e_phone.insert(0, member.phone)
        e_phone.pack(fill="x", padx=30, pady=(2, 8))

        ctk.CTkLabel(popup, text="Assigned Coach:", font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", padx=30)
        trainer_choices = ["No Coach"] + [f"{t.person_id} - {t.name}" for t in self.gym.trainers]
        curr_tr = "No Coach"
        if member.trainer_id:
            found_t = self.gym.find_trainer_by_id(member.trainer_id)
            if found_t:
                curr_tr = f"{found_t.person_id} - {found_t.name}"

        cmb_tr = ctk.CTkOptionMenu(popup, values=trainer_choices)
        cmb_tr.set(curr_tr if curr_tr in trainer_choices else trainer_choices[0])
        cmb_tr.pack(fill="x", padx=30, pady=(2, 10))

        def save_changes():
            new_name = e_name.get().strip()
            new_phone = e_phone.get().strip()
            sel_tr = cmb_tr.get()

            if not new_name or not new_phone:
                messagebox.showerror("Error", "Name and Phone cannot be empty.")
                return

            try:
                self.gym.update_member(member.person_id, new_name, new_phone, member.membership_type)
                member.trainer_id = None if sel_tr == "No Coach" else int(sel_tr.split(" - ")[0])
                self.gym.save()

                popup.destroy()
                self.show_members()
                messagebox.showinfo("Success", f"Member #{member.person_id} updated!")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        ctk.CTkButton(popup, text="Save Updates", fg_color="#2563eb", hover_color="#1d4ed8", command=save_changes).pack(fill="x", padx=30, pady=15)

    def _delete_member(self, member_id: int):
        member = self.gym.find_member_by_id(member_id)
        name = member.name if member else str(member_id)
        if messagebox.askyesno("Confirm", f"Permanently delete member {name} (#{member_id})?"):
            try:
                self.gym.delete_member(member_id)
                self.show_members()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _action_freeze(self, member_id: int):
        try:
            self.gym.freeze_member_membership(member_id)
            sub = self.gym.get_latest_membership(member_id)
            messagebox.showinfo("Frozen", f"Membership FROZEN!\nRemaining sessions preserved: {sub.remaining_sessions}")
            self.show_members()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _action_unfreeze(self, member_id: int):
        try:
            self.gym.unfreeze_member_membership(member_id)
            sub = self.gym.get_latest_membership(member_id)
            messagebox.showinfo("Activated", f"Membership Unfrozen!\nNew End Date: {sub.end_date}")
            self.show_members()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_member_full_profile(self, member_id: int):
        try:
            p = self.gym.get_member_complete_profile(member_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        popup = ctk.CTkToplevel(self)
        popup.title(f"Profile — {p['name']} (#{p['id']})")
        popup.geometry("540x620")
        popup.grab_set()

        scroll = ctk.CTkScrollableFrame(popup, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(scroll, text=f"👤 {p['name']}", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(5, 2))
        ctk.CTkLabel(scroll, text=f"Member ID: #{p['id']} | Phone: {p['phone']}", text_color="#9ca3af").pack(anchor="w", pady=(0, 10))

        sub_card = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=8)
        sub_card.pack(fill="x", pady=8, padx=5)
        ctk.CTkLabel(sub_card, text="Subscription Details", font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=15, pady=(10, 5))

        lines = [
            f"• Status: {p['status']}",
            f"• Plan: {p['membership_plan']}",
            f"• Sessions: {p['remaining_sessions']} / {p['total_sessions']} Remaining",
            f"• Trainer: {p['trainer_assigned']} ({p['trainer_specialization']})",
            f"• Renewal Deadline: {p['renewal_deadline']}",
            f"• Last Attendance: {p['last_checkin']}",
            f"• Total Attendance Days: {p['total_attendance_days']} Days"
        ]
        for l in lines:
            ctk.CTkLabel(sub_card, text=l, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=2)

        inb_card = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=8)
        inb_card.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(inb_card, text="InBody Progress (Before vs After)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10b981").pack(anchor="w", padx=15, pady=(10, 5))

        prog = p["inbody_progress"]
        if "status" in prog:
            ctk.CTkLabel(inb_card, text="No InBody records registered yet.", text_color="gray").pack(padx=20, pady=10)
        else:
            w_diff = f"{prog['weight_change']:+0.1f} kg"
            fat_diff = f"{prog['fat_change']:+0.1f} %"
            mus_diff = f"{prog['muscle_change']:+0.1f} kg"
            summary = f"Total Scans: {prog['total_records']}\n• Weight Change: {w_diff}\n• Body Fat Change: {fat_diff}\n• Muscle Change: {mus_diff}"
            ctk.CTkLabel(inb_card, text=summary, font=ctk.CTkFont(size=13, weight="bold"), text_color="#e5e7eb", justify="left").pack(anchor="w", padx=20, pady=5)

    def _popup_add_member(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Register Member")
        popup.geometry("460x650")
        popup.grab_set()

        scroll = ctk.CTkScrollableFrame(popup, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(scroll, text="New Member Registration", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(5, 10))

        e_name = ctk.CTkEntry(scroll, placeholder_text="Full Name")
        e_name.pack(fill="x", padx=15, pady=6)

        e_phone = ctk.CTkEntry(scroll, placeholder_text="Phone Number (11 digits, starts with 01)")
        e_phone.pack(fill="x", padx=15, pady=6)

        plans_list = list(MEMBERSHIP_PLANS.keys())
        plan_var = ctk.StringVar(value=plans_list[0])
        e_plan = ctk.CTkOptionMenu(scroll, values=plans_list, variable=plan_var)
        e_plan.pack(fill="x", padx=15, pady=6)

        trainer_choices = ["No Coach (Standard Rate)"] + [f"{t.person_id} - {t.name} ({t.specialization})" for t in self.gym.trainers]
        trainer_var = ctk.StringVar(value=trainer_choices[0])
        e_trainer = ctk.CTkOptionMenu(scroll, values=trainer_choices, variable=trainer_var)
        e_trainer.pack(fill="x", padx=15, pady=6)

        inb_box = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=8)
        inb_box.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(inb_box, text="Initial InBody Details", font=ctk.CTkFont(size=13, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=10, pady=(6, 4))

        e_w = ctk.CTkEntry(inb_box, placeholder_text="Weight (kg)")
        e_w.pack(fill="x", padx=10, pady=3)
        e_h = ctk.CTkEntry(inb_box, placeholder_text="Height (cm)")
        e_h.pack(fill="x", padx=10, pady=3)
        e_fat = ctk.CTkEntry(inb_box, placeholder_text="Body Fat (%)")
        e_fat.pack(fill="x", padx=10, pady=3)
        e_mus = ctk.CTkEntry(inb_box, placeholder_text="Muscle Mass (kg)")
        e_mus.pack(fill="x", padx=10, pady=(3, 6))

        pay_method_var = ctk.StringVar(value="Cash")
        pay_menu = ctk.CTkOptionMenu(scroll, values=["Cash", "Visa", "Instapay", "Vodafone Cash"], variable=pay_method_var)
        pay_menu.pack(fill="x", padx=15, pady=6)

        lbl_price = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10b981")
        lbl_price.pack(pady=4)

        def sync_cost(*args):
            p_name = plan_var.get()
            has_tr = trainer_var.get() != "No Coach (Standard Rate)"
            base_p = MEMBERSHIP_PLANS[p_name]["price"]
            tax = (base_p * TRAINER_TAX_RATE) if has_tr else 0.0
            tot = base_p + tax
            tax_str = f" [Includes 10% Coach Fee: +${tax:.2f}]" if has_tr else ""
            lbl_price.configure(text=f"Total: ${tot:.2f}{tax_str}")

        plan_var.trace_add("write", sync_cost)
        trainer_var.trace_add("write", sync_cost)
        sync_cost()

        def save():
            try:
                name = e_name.get().strip()
                phone = e_phone.get().strip()
                plan = plan_var.get()
                tr_val = trainer_var.get()
                method = pay_method_var.get()
                tid = int(tr_val.split(" - ")[0]) if tr_val != "No Coach (Standard Rate)" else None

                w = float(e_w.get()) if e_w.get() else None
                h = float(e_h.get()) if e_h.get() else None
                fat = float(e_fat.get()) if e_fat.get() else None
                mus = float(e_mus.get()) if e_mus.get() else None

                m = self.gym.register_member(
                    name=name, phone=phone, plan_name=plan, payment_method=method,
                    trainer_id=tid, weight=w, height=h, fat_percentage=fat, muscle_mass=mus
                )
                popup.destroy()
                self.show_members()
                self._show_qr_popup(m)
                messagebox.showinfo("Success", f"Member {m.name} registered!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(scroll, text="Complete Enrollment", fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(weight="bold"), command=save).pack(fill="x", padx=15, pady=12)

    def _popup_renew_member_flow(self, member_id: int):
        member = self.gym.find_member_by_id(member_id)
        if not member:
            return

        popup = ctk.CTkToplevel(self)
        popup.title(f"Renew — {member.name}")
        popup.geometry("420x520")
        popup.grab_set()

        scroll = ctk.CTkScrollableFrame(popup, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(scroll, text=f"Renew: {member.name} (#{member.person_id})", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=10)

        plan_var = ctk.StringVar(value=list(MEMBERSHIP_PLANS.keys())[0])
        e_plan = ctk.CTkOptionMenu(scroll, values=list(MEMBERSHIP_PLANS.keys()), variable=plan_var)
        e_plan.pack(fill="x", padx=15, pady=6)

        inb_box = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=8)
        inb_box.pack(fill="x", padx=15, pady=8)
        ctk.CTkLabel(inb_box, text="Renewal InBody Progress", font=ctk.CTkFont(size=13, weight="bold"), text_color="#10b981").pack(anchor="w", padx=10, pady=(6, 4))

        e_w = ctk.CTkEntry(inb_box, placeholder_text="Weight (kg)")
        e_w.pack(fill="x", padx=10, pady=3)
        e_h = ctk.CTkEntry(inb_box, placeholder_text="Height (cm)")
        e_h.pack(fill="x", padx=10, pady=3)
        e_fat = ctk.CTkEntry(inb_box, placeholder_text="Fat (%)")
        e_fat.pack(fill="x", padx=10, pady=3)
        e_mus = ctk.CTkEntry(inb_box, placeholder_text="Muscles (kg)")
        e_mus.pack(fill="x", padx=10, pady=(3, 6))

        pay_var = ctk.StringVar(value="Cash")
        e_pay = ctk.CTkOptionMenu(scroll, values=["Cash", "Visa", "Instapay", "Vodafone Cash"], variable=pay_var)
        e_pay.pack(fill="x", padx=15, pady=6)

        def do_renew():
            try:
                w = float(e_w.get()) if e_w.get() else None
                h = float(e_h.get()) if e_h.get() else None
                fat = float(e_fat.get()) if e_fat.get() else None
                mus = float(e_mus.get()) if e_mus.get() else None

                sub = self.gym.renew_membership(
                    member_id=member_id, plan_name=plan_var.get(), payment_method=pay_var.get(),
                    weight=w, height=h, fat_percentage=fat, muscle_mass=mus
                )
                popup.destroy()
                self.show_members()
                messagebox.showinfo("Renewed", f"Renewed until {sub.end_date}!\nSessions: {sub.remaining_sessions}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(scroll, text="Confirm Renewal", fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=do_renew).pack(fill="x", padx=15, pady=12)

    def _show_qr_popup(self, member: Member):
        qr_path = QRManager.generate_qr(member.person_id, member.qr_token)
        popup = ctk.CTkToplevel(self)
        popup.title(f"QR — {member.name}")
        popup.geometry("320x390")
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"{member.name} (#{member.person_id})", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=12)
        try:
            pil_img = Image.open(qr_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(190, 190))
            ctk.CTkLabel(popup, image=ctk_img, text="").pack(pady=8)
        except Exception as e:
            ctk.CTkLabel(popup, text=f"Error displaying image: {e}").pack(pady=10)

    # =============================================================
    # 3. Trainers
    # =============================================================
    def show_trainers(self):
        self._clear_main()

        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(top_bar, text="Trainers Management", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkButton(top_bar, text="+ Add Trainer", fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(weight="bold"), command=self._popup_add_trainer).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        if not self.gym.trainers:
            ctk.CTkLabel(scroll, text="No trainers registered yet.", text_color="gray").pack(pady=40)
            return

        for t in self.gym.trainers:
            row = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=8)
            row.pack(fill="x", pady=5, padx=5)

            trainees = [m for m in self.gym.members if m.trainer_id == t.person_id]
            ctk.CTkButton(row, text="View Results", width=130, fg_color="#8b5cf6", hover_color="#7c3aed", font=ctk.CTkFont(weight="bold"), command=lambda tid=t.person_id: self._show_trainer_trainees_modal(tid)).pack(side="right", padx=15, pady=10)
            ctk.CTkLabel(row, text=f"Trainees: {len(trainees)}", font=ctk.CTkFont(weight="bold"), text_color="#60a5fa").pack(side="right", padx=15, pady=10)

            info = f"#{t.person_id} | Coach: {t.name} | 📞 {t.phone} | Specialty: {t.specialization} | Salary: ${t.salary:,.2f}"
            ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=10)

    def _show_trainer_trainees_modal(self, trainer_id: int):
        try:
            rep = self.gym.get_trainer_trainees_report(trainer_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        popup = ctk.CTkToplevel(self)
        popup.title(f"Coach {rep['trainer_name']} — Results")
        popup.geometry("640x540")
        popup.grab_set()

        scroll = ctk.CTkScrollableFrame(popup, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(scroll, text=f"Coach: {rep['trainer_name']} ({rep['specialization']})", font=ctk.CTkFont(size=18, weight="bold"), text_color="#38bdf8").pack(anchor="w", pady=(5, 5))

        if not rep["trainees"]:
            ctk.CTkLabel(scroll, text="No trainees currently assigned to this coach.", text_color="gray").pack(pady=30)
            return

        for tr in rep["trainees"]:
            card = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)

            ctk.CTkLabel(card, text=f"{tr['name']} (#{tr['member_id']}) — 📞 {tr['phone']}", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(8, 2))
            ctk.CTkLabel(card, text=f"• Attendance (3M): {tr['attendance_last_3_months']} Days | Sessions Remaining: {tr['remaining_sessions']}", font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", padx=20, pady=2)

            prog = tr["progress_before_and_after"]
            if "status" not in prog:
                res_txt = f"• Progress: Weight {prog['weight_change']:+0.1f}kg | Fat {prog['fat_change']:+0.1f}% | Muscle {prog['muscle_change']:+0.1f}kg"
                ctk.CTkLabel(card, text=res_txt, text_color="#10b981", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(2, 8))

    def _popup_add_trainer(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Trainer")
        popup.geometry("380x380")
        popup.grab_set()

        ctk.CTkLabel(popup, text="Add New Trainer", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        auto_id = self.gym.generate_trainer_id()

        e_name = ctk.CTkEntry(popup, placeholder_text="Trainer Name")
        e_name.pack(fill="x", padx=30, pady=6)
        e_phone = ctk.CTkEntry(popup, placeholder_text="Phone Number")
        e_phone.pack(fill="x", padx=30, pady=6)
        e_spec = ctk.CTkOptionMenu(popup, values=["Iron / Bodybuilding", "Fitness", "Cardio", "Crossfit", "Boxing"])
        e_spec.pack(fill="x", padx=30, pady=6)
        e_sal = ctk.CTkEntry(popup, placeholder_text="Monthly Salary ($)")
        e_sal.pack(fill="x", padx=30, pady=6)

        def save():
            try:
                t = Trainer(auto_id, e_name.get().strip(), e_phone.get().strip(), e_spec.get(), float(e_sal.get().strip()))
                self.gym.add_trainer(t)
                popup.destroy()
                self.show_trainers()
                messagebox.showinfo("Success", f"Trainer {t.name} registered!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(popup, text="Save Trainer", fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(weight="bold"), command=save).pack(fill="x", padx=30, pady=15)

    # =============================================================
    # 4. Memberships
    # =============================================================
    def show_memberships(self):
        self._clear_main()

        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=25, pady=(20, 15))
        ctk.CTkLabel(top_bar, text="Memberships Ledger", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        if not self.gym.memberships:
            ctk.CTkLabel(scroll, text="No memberships recorded yet.", text_color="gray").pack(pady=40)
            return

        for ms in reversed(self.gym.memberships):
            row = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=8)
            row.pack(fill="x", pady=4, padx=5)

            st = getattr(ms, "status", "Active" if ms.is_active else "Expired")
            s_color = "#10b981" if st == "Active" else ("#f59e0b" if st == "Frozen" else "#ef4444")
            ctk.CTkLabel(row, text=st.upper(), fg_color=s_color, text_color="white", corner_radius=6, width=70, font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", padx=15, pady=10)

            m = self.gym.find_member_by_id(ms.member_id)
            name = m.name if m else "Unknown"
            info = f"Subscription #{ms.membership_id} | Member: #{ms.member_id} ({name}) | {ms.start_date} to {ms.end_date} | Sessions: {getattr(ms, 'remaining_sessions', 'N/A')}/{getattr(ms, 'total_sessions', 'N/A')} | Cost: ${ms.cost:,.2f}"
            ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=10)

    # =============================================================
    # 5. Attendance
    # =============================================================
    def show_attendance(self):
        self._clear_main()

        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        ctk.CTkLabel(header, text="Attendance Management", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        box = ctk.CTkFrame(self.main_frame, fg_color="#111827", corner_radius=10)
        box.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(box, text="Member ID:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(20, 5), pady=18)
        self.att_entry = ctk.CTkEntry(box, placeholder_text="e.g. 10001", width=140, fg_color="#1f2937")
        self.att_entry.pack(side="left", padx=5, pady=18)
        self.att_entry.bind("<Return>", lambda e: self._handle_manual_checkin())

        ctk.CTkButton(box, text="Check-in & Deduct", fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=self._handle_manual_checkin).pack(side="left", padx=6, pady=18)
        ctk.CTkButton(box, text="📁 Scan QR Image", fg_color="#4338ca", hover_color="#3730a3", command=self._handle_qr_file_checkin).pack(side="left", padx=6, pady=18)
        ctk.CTkButton(box, text="📷 Instant Webcam", fg_color="#2563eb", hover_color="#1d4ed8", command=self._handle_webcam_checkin).pack(side="left", padx=6, pady=18)

        ctk.CTkLabel(self.main_frame, text="Current Active Floor (Auto-clears after 2 hours)", font=ctk.CTkFont(size=15, weight="bold"), text_color="#f59e0b").pack(anchor="w", padx=25, pady=(15, 10))

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        in_gym_now = self.gym.get_currently_in_gym()
        if not in_gym_now:
            ctk.CTkLabel(scroll, text="No members currently on the gym floor (No check-ins within the last 2 hours).", text_color="gray").pack(pady=40)
            return

        for p in in_gym_now:
            row = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=6)
            row.pack(fill="x", pady=4, padx=5)
            ctk.CTkLabel(row, text=f"Inside: {p['duration_minutes']} min", text_color="#2dd4bf", font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=15, pady=8)
            ctk.CTkLabel(row, text=f"#{p['member_id']} | {p['member_name']} | Entered: {p['check_in_time']}", font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=8)

    def _execute_checkin(self, member_id: int):
        try:
            att = self.gym.record_attendance(member_id)
            m = self.gym.find_member_by_id(member_id)
            sub = self.gym.get_active_membership(member_id)
            rem = getattr(sub, "remaining_sessions", 0) if sub else 0
            self.att_entry.delete(0, "end")
            self.show_attendance()
            messagebox.showinfo("Access Granted", f"Welcome, {m.name}!\nTime: {att.timestamp}\n1 Session Deducted.\nRemaining: {rem}")
        except ValueError as e:
            messagebox.showerror("Access Denied", str(e))

    def _handle_manual_checkin(self):
        val = self.att_entry.get().strip()
        if not val or not val.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid numeric Member ID.")
            return
        self._execute_checkin(int(val))

    def _handle_qr_file_checkin(self):
        file_path = filedialog.askopenfilename(
            title="Select QR Image", initialdir=QRManager.QR_FOLDER,
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return
        try:
            token = QRManager.decode_qr_image(file_path)
            att = self.gym.record_attendance_by_token(token)
            m = self.gym.find_member_by_token(token)
            self.show_attendance()
            messagebox.showinfo("QR Verified", f"Welcome, {m.name}!\n1 Session Deducted.")
        except Exception as e:
            messagebox.showerror("Scan Error", str(e))

    def _handle_webcam_checkin(self):
        try:
            token = QRManager.scan_from_webcam()
            if not token:
                return
            att = self.gym.record_attendance_by_token(token)
            m = self.gym.find_member_by_token(token)
            self.show_attendance()
            messagebox.showinfo("Webcam Scan", f"Welcome, {m.name}!\n1 Session Deducted.")
        except Exception as e:
            messagebox.showerror("Access Denied", str(e))

    # =============================================================
    # 6. Financial Ledger (تدقيق أمان فوري + تعديل وسيلة الدفع والمبلغ + حذف)
    # =============================================================
    def show_payments(self):
        self._clear_main()

        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=25, pady=(20, 15))
        ctk.CTkLabel(top_bar, text="Financial Ledger & Income Tracking", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        box = ctk.CTkFrame(self.main_frame, fg_color="#111827", corner_radius=10)
        box.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(box, text="Member ID:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5), pady=18)
        self.p_mid = ctk.CTkEntry(box, placeholder_text="e.g. 10001", width=110, fg_color="#1f2937")
        self.p_mid.pack(side="left", padx=5, pady=18)

        self.lbl_member_verify = ctk.CTkLabel(box, text="[Enter valid ID]", font=ctk.CTkFont(size=11), text_color="#9ca3af")
        self.lbl_member_verify.pack(side="left", padx=5, pady=18)

        def verify_member_realtime(*args):
            raw = self.p_mid.get().strip()
            if raw.isdigit():
                m = self.gym.find_member_by_id(int(raw))
                if m:
                    self.lbl_member_verify.configure(text=f"✓ {m.name}", text_color="#10b981")
                    return
            self.lbl_member_verify.configure(text="✗ Not found", text_color="#ef4444")

        self.p_mid.bind("<KeyRelease>", verify_member_realtime)

        ctk.CTkLabel(box, text="Amount ($):", font=ctk.CTkFont(size=13)).pack(side="left", padx=(10, 5), pady=18)
        self.p_amt = ctk.CTkEntry(box, placeholder_text="e.g. 300", width=90, fg_color="#1f2937")
        self.p_amt.pack(side="left", padx=5, pady=18)

        self.p_method = ctk.CTkOptionMenu(box, values=["Cash", "Visa", "Instapay", "Vodafone Cash"], width=130)
        self.p_method.pack(side="left", padx=8, pady=18)

        self.p_ref = ctk.CTkEntry(box, placeholder_text="Description / Ref", width=150, fg_color="#1f2937")
        self.p_ref.pack(side="left", padx=6, pady=18)

        ctk.CTkButton(box, text="Record Payment", fg_color="#2563eb", hover_color="#1d4ed8", font=ctk.CTkFont(weight="bold"), command=self._handle_manual_payment).pack(side="left", padx=8, pady=18)

        ctk.CTkLabel(self.main_frame, text="All Transactions History (Editable & Removable)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=25, pady=(15, 10))

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        if not self.gym.payments:
            ctk.CTkLabel(scroll, text="No payment records found.", text_color="gray").pack(pady=40)
            return

        for p in reversed(self.gym.payments):
            row = ctk.CTkFrame(scroll, fg_color="#1f2937", corner_radius=6)
            row.pack(fill="x", pady=4, padx=5)

            ctk.CTkButton(row, text="Delete", width=55, fg_color="#dc2626", hover_color="#b91c1c", command=lambda pid=p.payment_id: self._delete_payment(pid)).pack(side="right", padx=(4, 10), pady=10)
            ctk.CTkButton(row, text="Edit", width=55, fg_color="#2563eb", hover_color="#1d4ed8", command=lambda pay=p: self._popup_edit_payment(pay)).pack(side="right", padx=4, pady=10)

            ctk.CTkLabel(row, text=f"${p.amount:,.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10b981").pack(side="right", padx=10, pady=10)
            ref_str = f" | {p.reference_number}" if p.reference_number else ""
            ctk.CTkLabel(row, text=f"{p.method}{ref_str} | {p.date}", text_color="#9ca3af").pack(side="right", padx=15, pady=10)

            m = self.gym.find_member_by_id(p.member_id)
            name = m.name if m else "Unknown"
            info = f"Receipt #{p.payment_id} | Member #{p.member_id} ({name})"
            ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=15, pady=10)

    def _handle_manual_payment(self):
        raw_mid = self.p_mid.get().strip()
        raw_amt = self.p_amt.get().strip()
        method = self.p_method.get()
        ref = self.p_ref.get().strip() or "Manual Payment"

        if not raw_mid or not raw_mid.isdigit() or not raw_amt:
            messagebox.showwarning("Warning", "Please provide a valid numeric Member ID and Amount.")
            return

        mid = int(raw_mid)
        member = self.gym.find_member_by_id(mid)
        if not member:
            messagebox.showerror("Invalid Member", f"Error: Member #{mid} does NOT exist in the database!\nCannot record a payment for a non-existent member.")
            return

        try:
            amt = float(raw_amt)
            if amt <= 0:
                messagebox.showerror("Error", "Payment amount must be greater than zero.")
                return

            p = self.gym.record_payment(mid, amt, method=method, ref=ref)
            self.p_mid.delete(0, "end")
            self.p_amt.delete(0, "end")
            self.p_ref.delete(0, "end")
            self.lbl_member_verify.configure(text="[Enter valid ID]", text_color="#9ca3af")
            self.show_payments()
            messagebox.showinfo("Success", f"Payment #{p.payment_id} of ${amt:,.2f} recorded for {member.name}!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _popup_edit_payment(self, payment: Payment):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Edit Payment #{payment.payment_id}")
        popup.geometry("360x340")
        popup.grab_set()

        m = self.gym.find_member_by_id(payment.member_id)
        m_name = m.name if m else "Unknown"

        ctk.CTkLabel(popup, text=f"Edit Receipt #{payment.payment_id}", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=12)
        ctk.CTkLabel(popup, text=f"Member: {m_name} (#{payment.member_id})", text_color="#9ca3af").pack(pady=(0, 10))

        e_amt = ctk.CTkEntry(popup)
        e_amt.insert(0, str(payment.amount))
        e_amt.pack(fill="x", padx=30, pady=6)

        cmb_method = ctk.CTkOptionMenu(popup, values=["Cash", "Visa", "Instapay", "Vodafone Cash"])
        cmb_method.set(payment.method.title())
        cmb_method.pack(fill="x", padx=30, pady=6)

        e_ref = ctk.CTkEntry(popup)
        e_ref.insert(0, payment.reference_number or "")
        e_ref.pack(fill="x", padx=30, pady=6)

        def save_pay_edit():
            try:
                new_amt = float(e_amt.get().strip())
                new_m = cmb_method.get()
                new_r = e_ref.get().strip()

                if hasattr(self.gym, "update_payment"):
                    self.gym.update_payment(payment.payment_id, new_amt, new_m, new_r)
                else:
                    payment.amount = new_amt
                    payment.method = new_m
                    payment.reference_number = new_r
                    self.gym.save()

                popup.destroy()
                self.show_payments()
                messagebox.showinfo("Updated", f"Receipt #{payment.payment_id} updated successfully!")
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        ctk.CTkButton(popup, text="Save Payment Changes", fg_color="#2563eb", hover_color="#1d4ed8", command=save_pay_edit).pack(fill="x", padx=30, pady=15)

    def _delete_payment(self, payment_id: int):
        if messagebox.askyesno("Confirm Deletion", f"Permanently delete payment receipt #{payment_id}?"):
            try:
                if hasattr(self.gym, "delete_payment"):
                    self.gym.delete_payment(payment_id)
                else:
                    self.gym.payments = [p for p in self.gym.payments if p.payment_id != payment_id]
                    self.gym.save()
                self.show_payments()
                messagebox.showinfo("Deleted", f"Receipt #{payment_id} has been removed.")
            except Exception as e:
                messagebox.showerror("Error", str(e))



def launch_app():
    app = GymApp()
    app.mainloop()


if __name__ == "__main__":
    launch_app()
"""
ui/dashboard_view.py - Modern Dashboard for Chiikawa Study Planner
Spacious productivity dashboard with daily metrics, interactive tasks, deadlines, and quick capture.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date, timedelta
from typing import Callable, Any
from theme import Theme
import database
import assets_mgr
import icons
from ui.components.modal import TaskModal
from ui.components.toast import ToastNotification


class DashboardView(ctk.CTkFrame):
    """Modern Dashboard showcasing daily progress, tasks, deadlines, and hero greeting."""

    def __init__(self, parent: Any, on_navigate: Callable[[str], None]):
        colors = Theme.current()
        super().__init__(parent, fg_color="transparent")
        self.on_navigate = on_navigate

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
        )
        self.scroll.pack(fill="both", expand=True, padx=24, pady=16)

        # 1. Hero Greeting Banner Card
        self.banner = ctk.CTkFrame(
            self.scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        self.banner.pack(fill="x", pady=(0, 16))

        banner_inner = ctk.CTkFrame(self.banner, fg_color="transparent")
        banner_inner.pack(fill="both", expand=True, padx=22, pady=18)

        text_box = ctk.CTkFrame(banner_inner, fg_color="transparent")
        text_box.pack(side="left", fill="both", expand=True)

        self.lbl_greeting = ctk.CTkLabel(
            text_box,
            text="",
            font=Theme.font_title(),
            text_color=colors["text_primary"],
            anchor="w"
        )
        self.lbl_greeting.pack(anchor="w")

        self.lbl_quote = ctk.CTkLabel(
            text_box,
            text="'Wakannai kedo, nantoka nare!' — Somehow it will all work out! Take one step at a time.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"],
            anchor="w"
        )
        self.lbl_quote.pack(anchor="w", pady=(4, 14))

        btn_row = ctk.CTkFrame(text_box, fg_color="transparent")
        btn_row.pack(anchor="w")

        ic_plus = icons.get_icon("plus", size=14, color="#FFFFFF")
        self.btn_new_task = ctk.CTkButton(
            btn_row,
            text=" New Task",
            image=ic_plus,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=34,
            width=120,
            command=self._open_new_task_modal
        )
        self.btn_new_task.pack(side="left", padx=(0, 10))

        ic_play = icons.get_icon("play", size=12, color=colors["text_primary"])
        self.btn_start_focus = ctk.CTkButton(
            btn_row,
            text=" Focus Timer",
            image=ic_play,
            compound="left",
            font=Theme.font_body(),
            fg_color=colors["bg_card_secondary"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=10,
            height=34,
            width=125,
            command=lambda: self.on_navigate("pomodoro")
        )
        self.btn_start_focus.pack(side="left")

        # Fast pre-cached mascot image
        banner_img = assets_mgr.get_illustration("laptop", size=(110, 110))
        if banner_img:
            lbl_banner_img = ctk.CTkLabel(banner_inner, image=banner_img, text="")
            lbl_banner_img.pack(side="right", padx=(10, 0))

        # 2. Key Metrics Row (4 modern cards)
        self.metrics_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.metrics_frame.pack(fill="x", pady=(0, 16))
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.metric_cards = []
        metric_configs = [
            ("Today's Tasks", "0 / 0", colors["accent_pink"], "tasks"),
            ("Study Time Today", "0m", colors["accent_blue"], "time"),
            ("Daily Progress", "0%", colors["accent_mint"], "progress"),
            ("Habit Streak", "Active", colors["accent_yellow"], "streak")
        ]

        for i, (title, default_val, accent_color, key) in enumerate(metric_configs):
            card = ctk.CTkFrame(
                self.metrics_frame,
                fg_color=colors["bg_card"],
                corner_radius=14,
                border_width=1,
                border_color=colors["border"]
            )
            card.grid(row=0, column=i, sticky="nsew", padx=4 if i in (1, 2) else (0 if i == 0 else 4))

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=16, pady=12, fill="both")

            lbl_t = ctk.CTkLabel(inner, text=title, font=Theme.font_small(), text_color=colors["text_secondary"], anchor="w")
            lbl_t.pack(anchor="w")

            lbl_v = ctk.CTkLabel(inner, text=default_val, font=Theme.font_header(), text_color=colors["text_primary"], anchor="w")
            lbl_v.pack(anchor="w", pady=(3, 0))

            bar = ctk.CTkProgressBar(inner, height=5, corner_radius=3, fg_color=colors["bg_card_secondary"], progress_color=accent_color)
            bar.pack(fill="x", pady=(8, 0))
            bar.set(0.0)

            self.metric_cards.append({"title": lbl_t, "value": lbl_v, "bar": bar, "key": key})

        # 3. Two Column Area: Tasks (Left) & Upcoming Deadlines + Quick Capture (Right)
        self.columns_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.columns_frame.pack(fill="both", expand=True)
        self.columns_frame.grid_columnconfigure(0, weight=6)
        self.columns_frame.grid_columnconfigure(1, weight=4)

        # Left Column: Today's Tasks
        left_col = ctk.CTkFrame(
            self.columns_frame,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        left_header = ctk.CTkFrame(left_col, fg_color="transparent")
        left_header.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(left_header, text="Today's Schedule & Tasks", font=Theme.font_header(), text_color=colors["text_primary"]).pack(side="left")

        btn_view_all = ctk.CTkButton(
            left_header,
            text="View All →",
            font=Theme.font_small(),
            width=70,
            height=26,
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["accent_pink"],
            command=lambda: self.on_navigate("todo")
        )
        btn_view_all.pack(side="right")

        self.tasks_container = ctk.CTkFrame(left_col, fg_color="transparent")
        self.tasks_container.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        # Right Column
        right_col = ctk.CTkFrame(self.columns_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Upcoming Deadlines Card
        upcoming_card = ctk.CTkFrame(
            right_col,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        upcoming_card.pack(fill="x", pady=(0, 16))

        up_header = ctk.CTkFrame(upcoming_card, fg_color="transparent")
        up_header.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(up_header, text="Upcoming Deadlines (7 Days)", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(side="left")

        self.upcoming_container = ctk.CTkFrame(upcoming_card, fg_color="transparent")
        self.upcoming_container.pack(fill="x", padx=16, pady=(0, 12))

        # Quick Capture Card
        capture_card = ctk.CTkFrame(
            right_col,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        capture_card.pack(fill="x")

        cap_header = ctk.CTkFrame(capture_card, fg_color="transparent")
        cap_header.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(cap_header, text="Quick Capture Note", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(side="left")

        self.ent_quick_capture = ctk.CTkEntry(
            capture_card,
            placeholder_text="Jot down a quick thought or reminder...",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_quick_capture.pack(fill="x", padx=16, pady=(0, 8))
        self.ent_quick_capture.bind("<Return>", lambda e: self._save_quick_capture())

        btn_cap = ctk.CTkButton(
            capture_card,
            text="Save Note",
            font=Theme.font_small(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=30,
            command=self._save_quick_capture
        )
        btn_cap.pack(anchor="e", padx=16, pady=(0, 12))

    def refresh(self):
        """Reload dynamic data cleanly."""
        colors = Theme.current()
        stats = database.get_dashboard_stats()
        user_name = database.get_setting("user_name", "Chiikawa Friend")

        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greet = "Good morning"
        elif 12 <= hour < 18:
            time_greet = "Good afternoon"
        else:
            time_greet = "Good evening"

        self.lbl_greeting.configure(text=f"{time_greet}, {user_name}")

        today_tot = stats["today_total"]
        today_comp = stats["today_completed"]
        rate = stats["today_rate"]
        study_mins = stats["study_minutes_today"]
        hrs = study_mins // 60
        mins = study_mins % 60
        time_display = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"

        for m in self.metric_cards:
            if m["key"] == "tasks":
                m["value"].configure(text=f"{today_comp} / {today_tot}")
                m["bar"].set(min(1.0, today_comp / max(1, today_tot)))
            elif m["key"] == "time":
                m["value"].configure(text=time_display)
                m["bar"].set(min(1.0, study_mins / 120.0))
            elif m["key"] == "progress":
                m["value"].configure(text=f"{rate}%")
                m["bar"].set(rate / 100.0)
            elif m["key"] == "streak":
                m["value"].configure(text="Consistent")
                m["bar"].set(0.85)

        # Refresh tasks
        for child in self.tasks_container.winfo_children():
            child.destroy()

        today_str = date.today().isoformat()
        today_tasks = database.get_tasks(due_date=today_str)

        if not today_tasks:
            empty_box = ctk.CTkFrame(self.tasks_container, fg_color="transparent")
            empty_box.pack(fill="x", pady=20)
            
            passed_img = assets_mgr.get_illustration("passed", size=(65, 65))
            if passed_img:
                lbl_e_img = ctk.CTkLabel(empty_box, image=passed_img, text="")
                lbl_e_img.pack()

            ctk.CTkLabel(
                empty_box,
                text="No tasks due today or all completed!\nChiikawa is cheering for you.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"],
                justify="center"
            ).pack(pady=(6, 0))
        else:
            for task in today_tasks[:6]:
                self._render_task_item(task)

        # Refresh upcoming deadlines
        for child in self.upcoming_container.winfo_children():
            child.destroy()

        upcoming = stats["upcoming_tasks"] + stats["upcoming_events"]
        def get_date(item):
            return item.get("due_date") or item.get("start_date") or ""
        upcoming.sort(key=get_date)

        if not upcoming:
            ctk.CTkLabel(
                self.upcoming_container,
                text="No deadlines within the next 7 days.",
                font=Theme.font_small(),
                text_color=colors["text_secondary"]
            ).pack(anchor="w", pady=6)
        else:
            for item in upcoming[:5]:
                self._render_upcoming_item(item)

    def _render_task_item(self, task: dict):
        colors = Theme.current()
        task_id = task["id"]
        is_done = bool(task["completed"])

        item_frame = ctk.CTkFrame(
            self.tasks_container,
            fg_color=colors["bg_card_secondary"] if is_done else colors["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=colors["border_subtle"]
        )
        item_frame.pack(fill="x", pady=3)

        row = ctk.CTkFrame(item_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=7)

        var_chk = tk.BooleanVar(value=is_done)
        chk = ctk.CTkCheckBox(
            row,
            text="",
            variable=var_chk,
            width=22,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            border_color=colors["border"],
            command=lambda tid=task_id, v=var_chk: self._toggle_task(tid, v.get())
        )
        chk.pack(side="left", padx=(0, 8))

        lbl_title = ctk.CTkLabel(
            row,
            text=task["title"],
            font=Theme.font_body(),
            text_color=colors["text_muted"] if is_done else colors["text_primary"],
            anchor="w"
        )
        lbl_title.pack(side="left", fill="x", expand=True)

        prio = task.get("priority", "Medium")
        prio_color = colors["accent_yellow"]
        if prio == "High":
            prio_color = colors["accent_pink"]
        elif prio == "Low":
            prio_color = colors["accent_mint"]

        lbl_prio = ctk.CTkLabel(
            row,
            text=prio,
            font=Theme.font_tag(),
            text_color=colors["text_primary"],
            fg_color=colors["bg_card_secondary"],
            corner_radius=5,
            padx=7,
            pady=2
        )
        lbl_prio.pack(side="right", padx=(6, 0))

        if task.get("subject_name"):
            lbl_sub = ctk.CTkLabel(
                row,
                text=task['subject_name'],
                font=Theme.font_tag(),
                text_color=colors["text_secondary"],
                fg_color=colors["bg_card_secondary"],
                corner_radius=5,
                padx=6,
                pady=2
            )
            lbl_sub.pack(side="right", padx=(6, 0))

    def _render_upcoming_item(self, item: dict):
        colors = Theme.current()
        item_date_str = item.get("due_date") or item.get("start_date") or ""
        title = item["title"]

        try:
            d_obj = datetime.strptime(item_date_str, "%Y-%m-%d").date()
            diff = (d_obj - date.today()).days
            if diff == 0:
                badge_text = "Today"
                badge_color = colors["accent_pink"]
            elif diff == 1:
                badge_text = "Tomorrow"
                badge_color = colors["accent_yellow"]
            else:
                badge_text = f"In {diff}d"
                badge_color = colors["accent_blue"]
        except Exception:
            badge_text = item_date_str
            badge_color = colors["border"]

        row = ctk.CTkFrame(self.upcoming_container, fg_color="transparent")
        row.pack(fill="x", pady=3)

        lbl_b = ctk.CTkLabel(
            row,
            text=badge_text,
            font=Theme.font_tag(),
            text_color="#FFFFFF" if badge_color == colors["accent_pink"] else colors["text_primary"],
            fg_color=badge_color,
            corner_radius=5,
            padx=6,
            pady=2,
            width=60
        )
        lbl_b.pack(side="left", padx=(0, 8))

        lbl_t = ctk.CTkLabel(
            row,
            text=title,
            font=Theme.font_small(),
            text_color=colors["text_primary"],
            anchor="w"
        )
        lbl_t.pack(side="left", fill="x", expand=True)

    def _toggle_task(self, task_id: int, new_val: bool):
        database.toggle_task_completed(task_id, new_val)
        msg = "Task completed!" if new_val else "Task marked active."
        ToastNotification.show(self.winfo_toplevel(), msg, color_theme="pink" if new_val else "blue")
        self.refresh()

    def _save_quick_capture(self):
        text = self.ent_quick_capture.get().strip()
        if not text:
            return
        database.add_note(title=f"Note ({date.today().strftime('%b %d')})", content=text, category="Quick Capture")
        self.ent_quick_capture.delete(0, "end")
        ToastNotification.show(self.winfo_toplevel(), "Saved to Notes.", color_theme="mint")

    def _open_new_task_modal(self):
        def on_saved(data):
            database.add_task(
                title=data["title"],
                description=data["description"],
                subject_id=data["subject_id"],
                category=data["category"],
                priority=data["priority"],
                due_date=data["due_date"],
                due_time=data["due_time"]
            )
            ToastNotification.show(self.winfo_toplevel(), "Task created.", color_theme="pink")
            self.refresh()

        TaskModal(self.winfo_toplevel(), on_saved)

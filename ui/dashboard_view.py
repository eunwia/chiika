"""
ui/dashboard_view.py - Modern Dashboard for Chiikawa Study Planner
Spacious productivity dashboard with daily metrics, interactive tasks, deadlines, and quick capture.
Refactored with reusable modern components: Card, StatCard, PrimaryButton, SecondaryButton, StyledEntry, StyledCheckBox, EmptyState.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date, timedelta
from typing import Callable, Any
from theme import Theme
import database
import assets_mgr
import icons
from ui.components.widgets import (
    Card,
    StatCard,
    PrimaryButton,
    SecondaryButton,
    GhostButton,
    StyledEntry,
    StyledCheckBox,
    EmptyState
)
from ui.components.modal import TaskModal
from ui.components.toast import ToastNotification


class DashboardView(ctk.CTkFrame):
    """Modern Dashboard showcasing daily progress, tasks, deadlines, and hero greeting."""

    def __init__(self, parent: Any, on_navigate: Callable[[str], None]):
        super().__init__(parent, fg_color="transparent")
        self.on_navigate = on_navigate

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.scroll.pack(fill="both", expand=True, padx=24, pady=16)

        # 1. Hero Greeting Banner Card
        self.banner = Card(
            self.scroll,
            corner_radius=Theme.RADIUS_XL,
            hoverable=False
        )
        self.banner.pack(fill="x", pady=(0, 18))

        banner_inner = ctk.CTkFrame(self.banner, fg_color="transparent")
        banner_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X + 4, pady=Theme.CARD_PAD_Y + 4)

        text_box = ctk.CTkFrame(banner_inner, fg_color="transparent")
        text_box.pack(side="left", fill="both", expand=True)

        self.lbl_greeting = ctk.CTkLabel(
            text_box,
            text="",
            font=Theme.font_page_title(),
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
        self.lbl_quote.pack(anchor="w", pady=(6, 16))

        btn_row = ctk.CTkFrame(text_box, fg_color="transparent")
        btn_row.pack(anchor="w")

        ic_plus = icons.get_icon("plus", size=16, color="#FFFFFF")
        self.btn_new_task = PrimaryButton(
            btn_row,
            text=" New Task",
            image=ic_plus,
            command=self._open_new_task_modal,
            width=136,
            height=Theme.BTN_HEIGHT
        )
        self.btn_new_task.pack(side="left", padx=(0, 12))

        ic_play = icons.get_icon("play", size=14, color=colors["text_primary"])
        self.btn_start_focus = SecondaryButton(
            btn_row,
            text=" Focus Timer",
            image=ic_play,
            command=lambda: self.on_navigate("pomodoro"),
            width=140,
            height=Theme.BTN_HEIGHT
        )
        self.btn_start_focus.pack(side="left")

        # Chiikawa mascot illustration
        banner_img = assets_mgr.get_illustration("laptop", size=(115, 115))
        if banner_img:
            self.lbl_banner_img = ctk.CTkLabel(banner_inner, image=banner_img, text="")
            self.lbl_banner_img.pack(side="right", padx=(12, 0))

        # 2. Key Metrics Row (4 modern StatCards)
        self.metrics_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.metrics_frame.pack(fill="x", pady=(0, 18))
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_tasks = StatCard(
            self.metrics_frame,
            title="Today's Tasks",
            value="0 / 0",
            accent_color=colors["accent_pink"],
            icon_name="tasks",
            progress=0.0
        )
        self.card_tasks.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_time = StatCard(
            self.metrics_frame,
            title="Study Time Today",
            value="0m",
            accent_color=colors["accent_blue"],
            icon_name="timer",
            progress=0.0
        )
        self.card_time.grid(row=0, column=1, sticky="nsew", padx=6)

        self.card_progress = StatCard(
            self.metrics_frame,
            title="Daily Progress",
            value="0%",
            accent_color=colors["accent_mint"],
            icon_name="progress",
            progress=0.0
        )
        self.card_progress.grid(row=0, column=2, sticky="nsew", padx=6)

        self.card_streak = StatCard(
            self.metrics_frame,
            title="Habit Consistency",
            value="Active",
            accent_color=colors["accent_yellow"],
            icon_name="habits",
            progress=0.85
        )
        self.card_streak.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        # 3. Two Column Area: Tasks (Left) & Upcoming Deadlines + Quick Capture (Right)
        self.columns_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.columns_frame.pack(fill="both", expand=True)
        self.columns_frame.grid_columnconfigure(0, weight=6)
        self.columns_frame.grid_columnconfigure(1, weight=4)

        # Left Column: Today's Tasks
        left_col = Card(
            self.columns_frame,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        left_header = ctk.CTkFrame(left_col, fg_color="transparent")
        left_header.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(Theme.CARD_PAD_Y, 10))

        ctk.CTkLabel(
            left_header,
            text="Today's Schedule & Tasks",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        btn_view_all = GhostButton(
            left_header,
            text="View All →",
            width=84,
            height=32,
            text_color=colors["accent_pink"],
            command=lambda: self.on_navigate("todo")
        )
        btn_view_all.pack(side="right")

        self.tasks_container = ctk.CTkFrame(left_col, fg_color="transparent")
        self.tasks_container.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=(0, Theme.CARD_PAD_Y))

        # Right Column
        right_col = ctk.CTkFrame(self.columns_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Upcoming Deadlines Card
        upcoming_card = Card(
            right_col,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        upcoming_card.pack(fill="x", pady=(0, 18))

        up_header = ctk.CTkFrame(upcoming_card, fg_color="transparent")
        up_header.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(Theme.CARD_PAD_Y, 8))
        ctk.CTkLabel(
            up_header,
            text="Upcoming Deadlines (7 Days)",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        self.upcoming_container = ctk.CTkFrame(upcoming_card, fg_color="transparent")
        self.upcoming_container.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(0, Theme.CARD_PAD_Y))

        # Quick Capture Card
        capture_card = Card(
            right_col,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        capture_card.pack(fill="x")

        cap_header = ctk.CTkFrame(capture_card, fg_color="transparent")
        cap_header.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(Theme.CARD_PAD_Y, 8))
        ctk.CTkLabel(
            cap_header,
            text="Quick Capture Note",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        self.ent_quick_capture = StyledEntry(
            capture_card,
            placeholder_text="Jot down a quick thought or reminder...",
            height=Theme.INPUT_HEIGHT
        )
        self.ent_quick_capture.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(0, 10))
        self.ent_quick_capture.bind("<Return>", lambda e: self._save_quick_capture())

        btn_cap = PrimaryButton(
            capture_card,
            text="Save Note",
            height=36,
            width=110,
            command=self._save_quick_capture
        )
        btn_cap.pack(anchor="e", padx=Theme.CARD_PAD_X, pady=(0, Theme.CARD_PAD_Y))

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

        self.lbl_greeting.configure(text=f"{time_greet}, {user_name} ✨")

        today_tot = stats["today_total"]
        today_comp = stats["today_completed"]
        rate = stats["today_rate"]
        study_mins = stats["study_minutes_today"]
        hrs = study_mins // 60
        mins = study_mins % 60
        time_display = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"

        # Update StatCards
        self.card_tasks.update_stat(
            value=f"{today_comp} / {today_tot}",
            progress=min(1.0, today_comp / max(1, today_tot))
        )
        self.card_time.update_stat(
            value=time_display,
            progress=min(1.0, study_mins / 120.0)
        )
        self.card_progress.update_stat(
            value=f"{rate}%",
            progress=rate / 100.0
        )
        self.card_streak.update_stat(
            value="Active",
            progress=0.85
        )

        # Refresh tasks
        for child in self.tasks_container.winfo_children():
            child.destroy()

        today_str = date.today().isoformat()
        today_tasks = database.get_tasks(due_date=today_str)

        if not today_tasks:
            empty = EmptyState(
                self.tasks_container,
                title="All caught up!",
                description="No tasks due today or all completed.\nChiikawa is cheering for you!",
                mascot_name="passed",
                action_text="+ Add a Task",
                action_command=self._open_new_task_modal
            )
            empty.pack(fill="x", pady=16)
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
                text="No upcoming deadlines within 7 days.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(anchor="w", pady=10)
        else:
            for item in upcoming[:5]:
                self._render_upcoming_item(item)

    def _render_task_item(self, task: dict):
        colors = Theme.current()
        task_id = task["id"]
        is_done = bool(task["completed"])

        item_frame = Card(
            self.tasks_container,
            fg_color=colors["bg_card_secondary"] if is_done else colors["bg_card"],
            corner_radius=Theme.RADIUS_MD,
            border_width=1,
            border_color=colors["border_subtle"],
            hoverable=True
        )
        item_frame.pack(fill="x", pady=4)

        row = ctk.CTkFrame(item_frame, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=10)

        var_chk = tk.BooleanVar(value=is_done)
        chk = StyledCheckBox(
            row,
            text="",
            variable=var_chk,
            command=lambda tid=task_id, v=var_chk: self._toggle_task(tid, v.get())
        )
        chk.pack(side="left", padx=(0, 10))

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
            corner_radius=6,
            padx=8,
            pady=3
        )
        lbl_prio.pack(side="right", padx=(8, 0))

        if task.get("subject_name"):
            lbl_sub = ctk.CTkLabel(
                row,
                text=task['subject_name'],
                font=Theme.font_tag(),
                text_color=colors["text_secondary"],
                fg_color=colors["bg_card_secondary"],
                corner_radius=6,
                padx=8,
                pady=3
            )
            lbl_sub.pack(side="right", padx=(8, 0))

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
        row.pack(fill="x", pady=4)

        lbl_b = ctk.CTkLabel(
            row,
            text=badge_text,
            font=Theme.font_tag(),
            text_color="#FFFFFF" if badge_color == colors["accent_pink"] else colors["text_primary"],
            fg_color=badge_color,
            corner_radius=6,
            padx=8,
            pady=3,
            width=65
        )
        lbl_b.pack(side="left", padx=(0, 10))

        lbl_t = ctk.CTkLabel(
            row,
            text=title,
            font=Theme.font_body(),
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

"""
ui/habit_view.py - Modern Habit Tracker View for Chiikawa Study Planner
Tracks daily habits, study consistency, streaks, and completion history with 7-day checkboxes.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date, timedelta
from typing import Dict, Any, List
from theme import Theme
import database
import icons
from ui.components.modal import HabitModal
from ui.components.toast import ToastNotification


class HabitView(ctk.CTkFrame):
    """Habit Tracker with 7-day interactive checkboxes, streaks, and consistency metrics."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 12))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Habit Tracker",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Build positive daily study routines and maintain consistency over time.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        ic_plus = icons.get_icon("plus", size=14, color="#FFFFFF")
        btn_add = ctk.CTkButton(
            header,
            text=" New Habit",
            image=ic_plus,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=36,
            command=self._open_add_habit_modal
        )
        btn_add.pack(side="right")

        self.content_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
        )
        self.content_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def refresh(self):
        colors = Theme.current()
        for child in self.content_scroll.winfo_children():
            child.destroy()

        habits = database.get_all_habits()

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        week_days = [start_of_week + timedelta(days=i) for i in range(7)]
        start_str = week_days[0].isoformat()
        end_str = week_days[-1].isoformat()

        habit_logs = database.get_habit_logs_for_range(start_str, end_str)

        # Weekly Consistency Card
        overview_card = ctk.CTkFrame(
            self.content_scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        overview_card.pack(fill="x", pady=(0, 14))

        ov_inner = ctk.CTkFrame(overview_card, fg_color="transparent")
        ov_inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            ov_inner,
            text=f"Weekly Routine: {start_of_week.strftime('%b %d')} - {week_days[-1].strftime('%b %d')}",
            font=Theme.font_header(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        total_possible = len(habits) * 7
        total_done = sum(len(dates) for dates in habit_logs.values())
        pct = int((total_done / total_possible * 100)) if total_possible > 0 else 0

        ctk.CTkLabel(
            ov_inner,
            text=f"Weekly Consistency: {total_done} of {total_possible} completed ({pct}%)",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 8))

        p_bar = ctk.CTkProgressBar(ov_inner, height=6, corner_radius=3, fg_color=colors["bg_card_secondary"], progress_color=colors["accent_pink"])
        p_bar.pack(fill="x")
        p_bar.set(pct / 100.0)

        if not habits:
            ctk.CTkLabel(
                self.content_scroll,
                text="No habits tracked yet. Click 'New Habit' to build your daily routine.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(pady=30)
            return

        # Table Card
        table_card = ctk.CTkFrame(
            self.content_scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        table_card.pack(fill="both", expand=True)

        header_row = ctk.CTkFrame(table_card, fg_color=colors["bg_card_secondary"], height=38, corner_radius=10)
        header_row.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(header_row, text="Habit Name", font=Theme.font_subheader(), text_color=colors["text_secondary"], width=200, anchor="w").pack(side="left", padx=12)

        days_box = ctk.CTkFrame(header_row, fg_color="transparent")
        days_box.pack(side="left", fill="x", expand=True)
        days_box.grid_columnconfigure(tuple(range(7)), weight=1)

        for col_idx, d_obj in enumerate(week_days):
            is_today = (d_obj == today)
            ctk.CTkLabel(
                days_box,
                text=f"{d_obj.strftime('%a')}\n{d_obj.day}",
                font=Theme.font_tag(),
                text_color=colors["accent_pink"] if is_today else colors["text_secondary"],
                justify="center"
            ).grid(row=0, column=col_idx, sticky="ew")

        ctk.CTkLabel(header_row, text="Streak", font=Theme.font_subheader(), text_color=colors["text_secondary"], width=80).pack(side="left", padx=10)
        ctk.CTkLabel(header_row, text="Actions", font=Theme.font_subheader(), text_color=colors["text_secondary"], width=50).pack(side="right", padx=(0, 10))

        for habit in habits:
            self._render_habit_row(table_card, habit, week_days, habit_logs.get(habit["id"], set()))

    def _render_habit_row(self, parent: Any, habit: dict, week_days: List[date], completed_dates: set):
        colors = Theme.current()
        hid = habit["id"]
        streak_info = database.get_habit_streak(hid)

        row_frame = ctk.CTkFrame(parent, fg_color="transparent", height=44)
        row_frame.pack(fill="x", padx=10, pady=3)

        info_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=200)
        info_box.pack(side="left", padx=12)
        info_box.pack_propagate(False)

        ctk.CTkLabel(info_box, text=habit["title"], font=Theme.font_body_bold(), text_color=colors["text_primary"], anchor="w").pack(fill="x", pady=6)

        chk_box = ctk.CTkFrame(row_frame, fg_color="transparent")
        chk_box.pack(side="left", fill="x", expand=True)
        chk_box.grid_columnconfigure(tuple(range(7)), weight=1)

        for col_idx, d_obj in enumerate(week_days):
            d_str = d_obj.isoformat()
            is_checked = (d_str in completed_dates)
            var_chk = tk.BooleanVar(value=is_checked)

            chk = ctk.CTkCheckBox(
                chk_box,
                text="",
                variable=var_chk,
                width=22,
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=5,
                fg_color=colors["accent_pink"],
                hover_color=colors["accent_pink_hover"],
                border_color=colors["border"],
                command=lambda h=hid, ds=d_str: self._toggle_habit(h, ds)
            )
            chk.grid(row=0, column=col_idx)

        streak_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=80)
        streak_box.pack(side="left", padx=10)
        streak_box.pack_propagate(False)

        cur_streak = streak_info["current"]
        streak_pill = ctk.CTkLabel(
            streak_box,
            text=f"{cur_streak} days",
            font=Theme.font_tag(),
            text_color="#FFFFFF" if cur_streak > 0 else colors["text_secondary"],
            fg_color=colors["accent_pink"] if cur_streak > 0 else colors["bg_card_secondary"],
            corner_radius=5,
            padx=7,
            pady=2
        )
        streak_pill.pack(anchor="center")

        ic_trash = icons.get_icon("trash", size=13, color="#D94161")
        btn_del = ctk.CTkButton(
            row_frame,
            text="",
            image=ic_trash,
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            command=lambda h=hid: self._delete_habit(h)
        )
        btn_del.pack(side="right", padx=(0, 10))

    def _toggle_habit(self, habit_id: int, log_date: str):
        database.toggle_habit_date(habit_id, log_date)
        self.refresh()

    def _delete_habit(self, habit_id: int):
        database.delete_habit(habit_id)
        ToastNotification.show(self.winfo_toplevel(), "Habit removed.", color_theme="blue")
        self.refresh()

    def _open_add_habit_modal(self):
        def on_saved(data):
            database.add_habit(
                title=data["title"],
                category=data["category"],
                target_frequency=data["target_frequency"],
                icon="⭐"
            )
            ToastNotification.show(self.winfo_toplevel(), "Habit added.", color_theme="pink")
            self.refresh()

        HabitModal(self.winfo_toplevel(), on_saved)

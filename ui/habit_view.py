"""
ui/habit_view.py - Modern Habit Tracker View for Chiikawa Study Planner
Tracks daily habits, study consistency, streaks, and completion history with 7-day checkboxes.
Refactored with PageHeader, Card, PrimaryButton, GhostButton, StyledCheckBox, and EmptyState.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date, timedelta
from typing import Dict, Any, List
from theme import Theme
import database
import icons
from ui.components.widgets import (
    PageHeader,
    Card,
    PrimaryButton,
    GhostButton,
    StyledCheckBox,
    EmptyState
)
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

        # 1. Page Header with Action Button
        header = PageHeader(
            self,
            title="Habit Tracker",
            subtitle="Build positive daily study routines and maintain consistency over time."
        )
        header.pack(fill="x", padx=24, pady=(20, 14))

        ic_plus = icons.get_icon("plus", size=16, color="#FFFFFF")
        btn_add = PrimaryButton(
            header.actions_container,
            text=" New Habit",
            image=ic_plus,
            command=self._open_add_habit_modal,
            width=136,
            height=Theme.BTN_HEIGHT
        )
        btn_add.pack(side="right")

        # 2. Main Scrollable Container
        self.content_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
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
        overview_card = Card(
            self.content_scroll,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        overview_card.pack(fill="x", pady=(0, 16))

        ov_inner = ctk.CTkFrame(overview_card, fg_color="transparent")
        ov_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=Theme.CARD_PAD_Y)

        ctk.CTkLabel(
            ov_inner,
            text=f"Weekly Routine: {start_of_week.strftime('%b %d')} - {week_days[-1].strftime('%b %d')}",
            font=Theme.font_card_title(),
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
        ).pack(anchor="w", pady=(3, 10))

        p_bar = ctk.CTkProgressBar(
            ov_inner,
            height=8,
            corner_radius=4,
            fg_color=colors["bg_card_secondary"],
            progress_color=colors["accent_pink"]
        )
        p_bar.pack(fill="x")
        p_bar.set(pct / 100.0)

        if not habits:
            empty = EmptyState(
                self.content_scroll,
                title="No habits tracked yet",
                description="Small daily steps lead to huge achievements.\nAdd your first habit routine to start your streak!",
                mascot_name="hya",
                action_text="+ Create Habit",
                action_command=self._open_add_habit_modal
            )
            empty.pack(fill="x", pady=24)
            return

        # Table Card
        table_card = Card(
            self.content_scroll,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        table_card.pack(fill="both", expand=True)

        header_row = ctk.CTkFrame(table_card, fg_color=colors["bg_card_secondary"], height=42, corner_radius=10)
        header_row.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(
            header_row,
            text="Habit Name",
            font=Theme.font_body_bold(),
            text_color=colors["text_secondary"],
            width=220,
            anchor="w"
        ).pack(side="left", padx=14)

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

        ctk.CTkLabel(
            header_row,
            text="Streak",
            font=Theme.font_body_bold(),
            text_color=colors["text_secondary"],
            width=90
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header_row,
            text="Actions",
            font=Theme.font_body_bold(),
            text_color=colors["text_secondary"],
            width=50
        ).pack(side="right", padx=(0, 14))

        for habit in habits:
            self._render_habit_row(table_card, habit, week_days, habit_logs.get(habit["id"], set()))

    def _render_habit_row(self, parent: Any, habit: dict, week_days: List[date], completed_dates: set):
        colors = Theme.current()
        hid = habit["id"]
        streak_info = database.get_habit_streak(hid)

        row_frame = ctk.CTkFrame(parent, fg_color="transparent", height=48)
        row_frame.pack(fill="x", padx=12, pady=3)

        info_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=220)
        info_box.pack(side="left", padx=14)
        info_box.pack_propagate(False)

        ctk.CTkLabel(
            info_box,
            text=habit["title"],
            font=Theme.font_body_bold(),
            text_color=colors["text_primary"],
            anchor="w"
        ).pack(fill="x", pady=8)

        chk_box = ctk.CTkFrame(row_frame, fg_color="transparent")
        chk_box.pack(side="left", fill="x", expand=True)
        chk_box.grid_columnconfigure(tuple(range(7)), weight=1)

        for col_idx, d_obj in enumerate(week_days):
            d_str = d_obj.isoformat()
            is_checked = (d_str in completed_dates)
            var_chk = tk.BooleanVar(value=is_checked)

            chk = StyledCheckBox(
                chk_box,
                text="",
                variable=var_chk,
                command=lambda h=hid, ds=d_str: self._toggle_habit(h, ds)
            )
            chk.grid(row=0, column=col_idx)

        streak_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=90)
        streak_box.pack(side="left", padx=10)
        streak_box.pack_propagate(False)

        cur_streak = streak_info["current"]
        streak_pill = ctk.CTkLabel(
            streak_box,
            text=f"{cur_streak} days",
            font=Theme.font_tag(),
            text_color="#FFFFFF" if cur_streak > 0 else colors["text_secondary"],
            fg_color=colors["accent_pink"] if cur_streak > 0 else colors["bg_card_secondary"],
            corner_radius=6,
            padx=8,
            pady=3
        )
        streak_pill.pack(anchor="center")

        ic_trash = icons.get_icon("trash", size=15, color=colors["priority_high_fg"])
        btn_del = GhostButton(
            row_frame,
            text="",
            image=ic_trash,
            width=32,
            height=32,
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

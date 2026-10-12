"""
ui/pomodoro_view.py - Modern Pomodoro Focus Timer for Chiikawa Study Planner
Features customizable focus & break durations, digital clock, progress tracking,
automatic SQLite session logging, and dynamic Chiikawa illustrations.
Refactored with PageHeader, Card, PrimaryButton, SecondaryButton, and modern typography.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Optional, Any
from theme import Theme
import database
import assets_mgr
import icons
from ui.components.widgets import PageHeader, Card, PrimaryButton, SecondaryButton
from ui.components.toast import ToastNotification


class PomodoroView(ctk.CTkFrame):
    """Pomodoro Focus Timer with animated progress and illustration states."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        
        self.mode = "focus"
        self.is_running = False
        self.timer_job = None

        self._load_settings()

        self.time_left = self.focus_duration
        self.total_time = self.focus_duration
        self.sessions_completed_today = 0

        self._build_ui()
        self.refresh()

    def _load_settings(self):
        focus_mins = int(database.get_setting("pomodoro_focus", "25"))
        short_mins = int(database.get_setting("pomodoro_short_break", "5"))
        long_mins = int(database.get_setting("pomodoro_long_break", "15"))

        self.focus_duration = focus_mins * 60
        self.short_break_duration = short_mins * 60
        self.long_break_duration = long_mins * 60

    def _build_ui(self):
        colors = Theme.current()

        # 1. Page Header
        header = PageHeader(
            self,
            title="Focus Timer",
            subtitle="Work in productive bursts with Chiikawa, take refreshing breaks to recharge."
        )
        header.pack(fill="x", padx=24, pady=(20, 20))

        # 2. Elevated Center Card
        center_card = Card(
            self,
            corner_radius=Theme.RADIUS_XL,
            hoverable=False
        )
        center_card.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        content = ctk.CTkFrame(center_card, fg_color="transparent")
        content.pack(pady=20)

        self.seg_mode = ctk.CTkSegmentedButton(
            content,
            values=["Focus", "Short Break", "Long Break"],
            font=Theme.font_body_bold(),
            height=40,
            corner_radius=12,
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card_secondary"],
            unselected_hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            command=self._on_mode_change
        )
        self.seg_mode.set("Focus")
        self.seg_mode.pack(pady=(0, 18))

        # Dynamic Chiikawa Mascot Image
        self.lbl_illustration = ctk.CTkLabel(content, text="")
        self.lbl_illustration.pack(pady=(0, 10))
        self._update_illustration()

        # Digital Countdown Display (56px bold)
        self.lbl_time = ctk.CTkLabel(
            content,
            text="25:00",
            font=Theme.font_timer(),
            text_color=colors["accent_pink"]
        )
        self.lbl_time.pack(pady=(0, 10))

        # Progress Bar (Substantial, rounded 10px)
        self.progress_bar = ctk.CTkProgressBar(
            content,
            width=420,
            height=10,
            corner_radius=5,
            fg_color=colors["bg_card_secondary"],
            progress_color=colors["accent_pink"]
        )
        self.progress_bar.pack(pady=(0, 18))
        self.progress_bar.set(1.0)

        # Subject Link Selector
        sub_row = ctk.CTkFrame(content, fg_color="transparent")
        sub_row.pack(pady=(0, 20))

        ctk.CTkLabel(
            sub_row,
            text="Course Focus:",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="left", padx=(0, 8))

        self.subjects = database.get_all_subjects()
        s_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        self.opt_subject = ctk.CTkOptionMenu(
            sub_row,
            values=s_names,
            font=Theme.font_body(),
            width=180,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"]
        )
        self.opt_subject.pack(side="left")

        # Timer Controls with larger min height 44px buttons
        ctrl_row = ctk.CTkFrame(content, fg_color="transparent")
        ctrl_row.pack(pady=(0, 14))

        self.ic_play = icons.get_icon("play", size=15, color="#FFFFFF")
        self.ic_pause = icons.get_icon("pause", size=15, color="#FFFFFF")
        self.btn_toggle = PrimaryButton(
            ctrl_row,
            text=" Start Focus",
            image=self.ic_play,
            command=self._toggle_timer,
            height=44,
            width=160
        )
        self.btn_toggle.pack(side="left", padx=8)

        ic_reset = icons.get_icon("rotate_ccw", size=15, color=colors["text_primary"])
        self.btn_reset = SecondaryButton(
            ctrl_row,
            text=" Reset",
            image=ic_reset,
            command=self._reset_timer,
            height=44,
            width=120
        )
        self.btn_reset.pack(side="left", padx=8)

        ic_skip = icons.get_icon("skip_forward", size=15, color=colors["text_primary"])
        self.btn_skip = SecondaryButton(
            ctrl_row,
            text=" Skip",
            image=ic_skip,
            command=self._skip_mode,
            height=44,
            width=110
        )
        self.btn_skip.pack(side="left", padx=8)

        self.lbl_sessions = ctk.CTkLabel(
            content,
            text="Completed Today: 0 Focus Sessions",
            font=Theme.font_tag(),
            text_color=colors["text_secondary"]
        )
        self.lbl_sessions.pack(pady=(8, 0))

    def _update_illustration(self):
        if self.mode == "focus":
            img = assets_mgr.get_illustration("study", size=(130, 130))
        elif self.mode == "short_break":
            img = assets_mgr.get_illustration("coffee", size=(130, 130))
        else:
            img = assets_mgr.get_illustration("books", size=(130, 130))

        if img:
            self.lbl_illustration.configure(image=img)

    def _on_mode_change(self, val: str):
        self._pause_timer()
        colors = Theme.current()
        if val == "Focus":
            self.mode = "focus"
            self.total_time = self.focus_duration
            self.lbl_time.configure(text_color=colors["accent_pink"])
            self.progress_bar.configure(progress_color=colors["accent_pink"])
            self.btn_toggle.configure(
                text=" Start Focus",
                fg_color=colors["accent_pink"],
                hover_color=colors["accent_pink_hover"]
            )
        elif val == "Short Break":
            self.mode = "short_break"
            self.total_time = self.short_break_duration
            self.lbl_time.configure(text_color=colors["accent_mint"])
            self.progress_bar.configure(progress_color=colors["accent_mint"])
            self.btn_toggle.configure(
                text=" Start Break",
                fg_color=colors["accent_mint"],
                hover_color=colors["accent_mint_hover"]
            )
        else:
            self.mode = "long_break"
            self.total_time = self.long_break_duration
            self.lbl_time.configure(text_color=colors["accent_blue"])
            self.progress_bar.configure(progress_color=colors["accent_blue"])
            self.btn_toggle.configure(
                text=" Start Long Break",
                fg_color=colors["accent_blue"],
                hover_color=colors["accent_blue_hover"]
            )

        self.time_left = self.total_time
        self._update_display()
        self._update_illustration()

    def _toggle_timer(self):
        if self.is_running:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self):
        self.is_running = True
        self.btn_toggle.configure(text=" Pause", image=self.ic_pause)
        self._tick()

    def _pause_timer(self):
        self.is_running = False
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        current_text = " Resume Focus" if self.mode == "focus" else " Resume Break"
        self.btn_toggle.configure(text=current_text, image=self.ic_play)

    def _reset_timer(self):
        self._pause_timer()
        self.time_left = self.total_time
        self._update_display()

    def _skip_mode(self):
        self._pause_timer()
        if self.mode == "focus":
            self.seg_mode.set("Short Break")
            self._on_mode_change("Short Break")
        else:
            self.seg_mode.set("Focus")
            self._on_mode_change("Focus")

    def _tick(self):
        if not self.is_running:
            return

        if self.time_left > 0:
            self.time_left -= 1
            self._update_display()
            self.timer_job = self.after(1000, self._tick)
        else:
            self._on_timer_complete()

    def _update_display(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.lbl_time.configure(text=f"{mins:02d}:{secs:02d}")
        if self.total_time > 0:
            self.progress_bar.set(self.time_left / self.total_time)

    def _on_timer_complete(self):
        self.is_running = False
        colors = Theme.current()

        if self.mode == "focus":
            self.sessions_completed_today += 1
            sel_sub_name = self.opt_subject.get()
            sub_id = None
            for s in self.subjects:
                if s["name"] == sel_sub_name:
                    sub_id = s["id"]
                    break

            mins_studied = self.focus_duration // 60
            database.log_study_session(
                subject_id=sub_id,
                topic=sel_sub_name if sub_id else "Focus Session",
                duration_minutes=mins_studied,
                session_type="Pomodoro"
            )
            ToastNotification.show(self.winfo_toplevel(), "Focus session finished! Time for a break.", color_theme="pink", duration_ms=4500)
            self.seg_mode.set("Short Break")
            self._on_mode_change("Short Break")
        else:
            ToastNotification.show(self.winfo_toplevel(), "Break over! Ready to focus again?", color_theme="mint", duration_ms=4500)
            self.seg_mode.set("Focus")
            self._on_mode_change("Focus")

        self.refresh()

    def refresh(self):
        stats = database.get_dashboard_stats()
        sessions = stats.get("sessions_today", 0)
        self.lbl_sessions.configure(text=f"Completed Today: {sessions} Focus Sessions")

        curr_sel = self.opt_subject.get()
        self.subjects = database.get_all_subjects()
        s_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        self.opt_subject.configure(values=s_names)
        if curr_sel in s_names:
            self.opt_subject.set(curr_sel)
        else:
            self.opt_subject.set(s_names[0])

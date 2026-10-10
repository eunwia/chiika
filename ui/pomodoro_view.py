"""
ui/pomodoro_view.py - Modern Pomodoro Focus Timer for Chiikawa Study Planner
Features customizable focus & break durations, digital clock, progress tracking,
automatic SQLite session logging, and dynamic Chiikawa illustrations with vector controls.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Optional, Any
from theme import Theme
import database
import assets_mgr
import icons
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

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 12))

        ctk.CTkLabel(
            header,
            text="Focus Timer",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Work in productive bursts with Chiikawa, take refreshing breaks to recharge.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        center_card = ctk.CTkFrame(
            self,
            fg_color=colors["bg_card"],
            corner_radius=20,
            border_width=1,
            border_color=colors["border"]
        )
        center_card.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        content = ctk.CTkFrame(center_card, fg_color="transparent")
        content.pack(expand=True, pady=15)

        self.seg_mode = ctk.CTkSegmentedButton(
            content,
            values=["Focus", "Short Break", "Long Break"],
            font=Theme.font_body_bold(),
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            command=self._on_mode_change,
            height=36
        )
        self.seg_mode.set("Focus")
        self.seg_mode.pack(pady=(0, 16))

        # Dynamic Chiikawa Mascot Image (Loads instantly <5ms from disk cache!)
        self.lbl_illustration = ctk.CTkLabel(content, text="")
        self.lbl_illustration.pack(pady=(0, 8))
        self._update_illustration()

        # Digital Countdown Display
        self.lbl_time = ctk.CTkLabel(
            content,
            text="25:00",
            font=Theme.font_timer(),
            text_color=colors["accent_pink"]
        )
        self.lbl_time.pack(pady=(0, 8))

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            content,
            width=360,
            height=8,
            corner_radius=4,
            fg_color=colors["bg_card_secondary"],
            progress_color=colors["accent_pink"]
        )
        self.progress_bar.pack(pady=(0, 16))
        self.progress_bar.set(1.0)

        # Subject Link Selector
        sub_row = ctk.CTkFrame(content, fg_color="transparent")
        sub_row.pack(pady=(0, 18))

        ctk.CTkLabel(sub_row, text="Course Focus:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 8))

        self.subjects = database.get_all_subjects()
        s_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        self.opt_subject = ctk.CTkOptionMenu(
            sub_row,
            values=s_names,
            font=Theme.font_small(),
            width=160,
            height=28,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"]
        )
        self.opt_subject.pack(side="left")

        # Timer Controls with Vector Icons
        ctrl_row = ctk.CTkFrame(content, fg_color="transparent")
        ctrl_row.pack(pady=(0, 10))

        self.ic_play = icons.get_icon("play", size=13, color="#FFFFFF")
        self.ic_pause = icons.get_icon("pause", size=13, color="#FFFFFF")
        self.btn_toggle = ctk.CTkButton(
            ctrl_row,
            text=" Start Focus",
            image=self.ic_play,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=12,
            height=40,
            width=140,
            command=self._toggle_timer
        )
        self.btn_toggle.pack(side="left", padx=6)

        ic_reset = icons.get_icon("rotate_ccw", size=13, color=colors["text_primary"])
        self.btn_reset = ctk.CTkButton(
            ctrl_row,
            text=" Reset",
            image=ic_reset,
            compound="left",
            font=Theme.font_body(),
            fg_color=colors["bg_card_secondary"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=12,
            height=40,
            width=100,
            command=self._reset_timer
        )
        self.btn_reset.pack(side="left", padx=6)

        ic_skip = icons.get_icon("skip_forward", size=13, color=colors["text_primary"])
        self.btn_skip = ctk.CTkButton(
            ctrl_row,
            text=" Skip",
            image=ic_skip,
            compound="left",
            font=Theme.font_body(),
            fg_color=colors["bg_card_secondary"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=12,
            height=40,
            width=90,
            command=self._skip_mode
        )
        self.btn_skip.pack(side="left", padx=6)

        self.lbl_sessions = ctk.CTkLabel(
            content,
            text="Completed Today: 0 Focus Sessions",
            font=Theme.font_tag(),
            text_color=colors["text_secondary"]
        )
        self.lbl_sessions.pack(pady=(8, 0))

    def _update_illustration(self):
        if self.mode == "focus":
            img = assets_mgr.get_illustration("study", size=(120, 120))
        elif self.mode == "short_break":
            img = assets_mgr.get_illustration("coffee", size=(120, 120))
        else:
            img = assets_mgr.get_illustration("books", size=(120, 120))

        if img:
            self.lbl_illustration.configure(image=img)

    def _on_mode_change(self, val: str):
        self._pause_timer()
        colors = Theme.current()
        if "Focus" in val:
            self.mode = "focus"
            self.total_time = self.focus_duration
            self.btn_toggle.configure(text=" Start Focus", image=self.ic_play, fg_color=colors["accent_pink"])
            self.progress_bar.configure(progress_color=colors["accent_pink"])
            self.lbl_time.configure(text_color=colors["accent_pink"])
        elif "Short" in val:
            self.mode = "short_break"
            self.total_time = self.short_break_duration
            self.btn_toggle.configure(text=" Start Break", image=self.ic_play, fg_color=colors["accent_mint"])
            self.progress_bar.configure(progress_color=colors["accent_mint"])
            self.lbl_time.configure(text_color=colors["accent_mint"])
        else:
            self.mode = "long_break"
            self.total_time = self.long_break_duration
            self.btn_toggle.configure(text=" Start Break", image=self.ic_play, fg_color=colors["accent_yellow"])
            self.progress_bar.configure(progress_color=colors["accent_yellow"])
            self.lbl_time.configure(text_color=colors["accent_yellow"])

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
        txt = " Resume" if self.time_left < self.total_time else " Start"
        self.btn_toggle.configure(text=txt, image=self.ic_play)

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
            self._on_timer_completed()

    def _update_display(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.lbl_time.configure(text=f"{mins:02d}:{secs:02d}")
        fraction = self.time_left / max(1, self.total_time)
        self.progress_bar.set(fraction)

    def _on_timer_completed(self):
        self._pause_timer()
        self.bell()

        if self.mode == "focus":
            self.sessions_completed_today += 1
            dur_mins = self.focus_duration // 60
            sel_sub_name = self.opt_subject.get()
            sub_id = None
            for s in self.subjects:
                if s["name"] == sel_sub_name:
                    sub_id = s["id"]
                    break

            database.log_study_session(
                subject_id=sub_id,
                topic="Pomodoro Focus Session",
                duration_minutes=dur_mins,
                session_type="Pomodoro",
                notes="Completed focus block"
            )

            ToastNotification.show(
                self.winfo_toplevel(),
                f"Focus session complete ({dur_mins} mins)! Take a well-deserved break.",
                color_theme="pink",
                duration_ms=4500
            )

            self.seg_mode.set("Short Break")
            self._on_mode_change("Short Break")
        else:
            ToastNotification.show(
                self.winfo_toplevel(),
                "Break completed. Ready to begin your next focus sprint?",
                color_theme="mint",
                duration_ms=4000
            )
            self.seg_mode.set("Focus")
            self._on_mode_change("Focus")

        self.refresh()

    def refresh(self):
        self._load_settings()
        today_str = date.today().isoformat()
        sessions = [s for s in database.get_study_sessions() if s.get("date") == today_str and s.get("session_type") == "Pomodoro"]
        self.sessions_completed_today = len(sessions)
        self.lbl_sessions.configure(text=f"Completed Today: {self.sessions_completed_today} Focus Sessions ({self.sessions_completed_today * (self.focus_duration // 60)} mins)")

        self.subjects = database.get_all_subjects()
        s_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        cur_sub = self.opt_subject.get()
        self.opt_subject.configure(values=s_names)
        if cur_sub in s_names:
            self.opt_subject.set(cur_sub)
        else:
            self.opt_subject.set("General (No Subject)")

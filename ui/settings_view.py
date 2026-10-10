"""
ui/settings_view.py - Modern Settings & Preferences View for Chiikawa Study Planner
Allows users to customize visual themes (Cozy Day / Cozy Night), Pomodoro timer durations,
user profile name, sound alerts, and sample data restoration.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Any
from theme import Theme
import database
import icons
from ui.components.toast import ToastNotification


class SettingsView(ctk.CTkFrame):
    """Settings view for theme customization, timer preferences, and database tools."""

    def __init__(self, parent: Any, on_theme_change: Callable[[str], None], on_reload_app: Callable[[], None]):
        super().__init__(parent, fg_color="transparent")
        self.on_theme_change = on_theme_change
        self.on_reload_app = on_reload_app

        self._build_ui()

    def _build_ui(self):
        colors = Theme.current()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 12))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Preferences & Settings",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Customize your visual theme, Pomodoro sprint lengths, and app profile.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
        )
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 1. Visual Theme Settings Card
        theme_card = ctk.CTkFrame(
            scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        theme_card.pack(fill="x", pady=(0, 16))

        th_inner = ctk.CTkFrame(theme_card, fg_color="transparent")
        th_inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(th_inner, text="Visual Theme Mode", font=Theme.font_header(), text_color=colors["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(
            th_inner,
            text="Choose between warm alabaster Cozy Day and deep twilight Cozy Night.",
            font=Theme.font_small(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 10))

        current_theme = database.get_setting("theme_mode", "light")
        self.seg_theme = ctk.CTkSegmentedButton(
            th_inner,
            values=["Cozy Day (Light)", "Cozy Night (Dark)"],
            font=Theme.font_body(),
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            command=self._handle_theme_change,
            height=36
        )
        init_sel = "Cozy Day (Light)" if current_theme == "light" else "Cozy Night (Dark)"
        self.seg_theme.set(init_sel)
        self.seg_theme.pack(anchor="w")

        # 2. Pomodoro Timer Customization Card
        pomo_card = ctk.CTkFrame(
            scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        pomo_card.pack(fill="x", pady=(0, 16))

        p_inner = ctk.CTkFrame(pomo_card, fg_color="transparent")
        p_inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(p_inner, text="Pomodoro Sprint Durations (Minutes)", font=Theme.font_header(), text_color=colors["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(
            p_inner,
            text="Configure your preferred focus intervals and short / long breaks.",
            font=Theme.font_small(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 12))

        inputs_grid = ctk.CTkFrame(p_inner, fg_color="transparent")
        inputs_grid.pack(fill="x", pady=(0, 12))
        inputs_grid.grid_columnconfigure((0, 1, 2), weight=1)

        f_box = ctk.CTkFrame(inputs_grid, fg_color="transparent")
        f_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_box, text="Focus Session (mins)", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w")
        self.ent_focus = ctk.CTkEntry(f_box, font=Theme.font_body(), fg_color=colors["input_bg"], border_color=colors["input_border"], height=34)
        self.ent_focus.insert(0, database.get_setting("pomodoro_focus", "25"))
        self.ent_focus.pack(fill="x", pady=(3, 0))

        s_box = ctk.CTkFrame(inputs_grid, fg_color="transparent")
        s_box.grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkLabel(s_box, text="Short Break (mins)", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w")
        self.ent_short = ctk.CTkEntry(s_box, font=Theme.font_body(), fg_color=colors["input_bg"], border_color=colors["input_border"], height=34)
        self.ent_short.insert(0, database.get_setting("pomodoro_short_break", "5"))
        self.ent_short.pack(fill="x", pady=(3, 0))

        l_box = ctk.CTkFrame(inputs_grid, fg_color="transparent")
        l_box.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(l_box, text="Long Break (mins)", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w")
        self.ent_long = ctk.CTkEntry(l_box, font=Theme.font_body(), fg_color=colors["input_bg"], border_color=colors["input_border"], height=34)
        self.ent_long.insert(0, database.get_setting("pomodoro_long_break", "15"))
        self.ent_long.pack(fill="x", pady=(3, 0))

        btn_save_timer = ctk.CTkButton(
            p_inner,
            text="Save Timer Durations",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=34,
            command=self._save_timer_settings
        )
        btn_save_timer.pack(anchor="w")

        # 3. User Profile Name Card
        prof_card = ctk.CTkFrame(
            scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        prof_card.pack(fill="x", pady=(0, 16))

        prof_inner = ctk.CTkFrame(prof_card, fg_color="transparent")
        prof_inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(prof_inner, text="User Display Name", font=Theme.font_header(), text_color=colors["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(
            prof_inner,
            text="Name used for personalized greetings on your dashboard.",
            font=Theme.font_small(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 8))

        name_row = ctk.CTkFrame(prof_inner, fg_color="transparent")
        name_row.pack(fill="x")

        self.ent_name = ctk.CTkEntry(
            name_row,
            placeholder_text="Your name...",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34,
            width=220
        )
        self.ent_name.insert(0, database.get_setting("user_name", "Chiikawa Friend"))
        self.ent_name.pack(side="left", padx=(0, 10))

        btn_save_name = ctk.CTkButton(
            name_row,
            text="Update Name",
            font=Theme.font_body(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=34,
            command=self._save_user_name
        )
        btn_save_name.pack(side="left")

        # 4. Data Tools & Reset Card
        data_card = ctk.CTkFrame(
            scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        data_card.pack(fill="x", pady=(0, 16))

        d_inner = ctk.CTkFrame(data_card, fg_color="transparent")
        d_inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(d_inner, text="Database Management & Sample Data", font=Theme.font_header(), text_color=colors["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(
            d_inner,
            text="Reload default sample subjects, tasks, and notes, or reset local database.",
            font=Theme.font_small(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 10))

        btn_row = ctk.CTkFrame(d_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_reload_sample = ctk.CTkButton(
            btn_row,
            text="Reload Sample Data",
            font=Theme.font_body(),
            fg_color=colors["bg_card_secondary"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=10,
            height=36,
            command=self._reload_sample_data
        )
        btn_reload_sample.pack(side="left", padx=(0, 10))

        btn_reset_all = ctk.CTkButton(
            btn_row,
            text="Reset to Defaults",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color="#FCE7EB",
            text_color="#D94161",
            border_width=1,
            border_color="#D94161",
            corner_radius=10,
            height=36,
            command=self._reset_all_data
        )
        btn_reset_all.pack(side="left")

    def _handle_theme_change(self, value: str):
        mode = "light" if "Day" in value else "dark"
        database.set_setting("theme_mode", mode)
        self.on_theme_change(mode)

    def _save_timer_settings(self):
        try:
            f = int(self.ent_focus.get().strip())
            s = int(self.ent_short.get().strip())
            l = int(self.ent_long.get().strip())
            if f <= 0 or s <= 0 or l <= 0:
                raise ValueError
        except ValueError:
            ToastNotification.show(self.winfo_toplevel(), "Please enter positive numbers for minutes.", color_theme="pink")
            return

        database.set_setting("pomodoro_focus", str(f))
        database.set_setting("pomodoro_short_break", str(s))
        database.set_setting("pomodoro_long_break", str(l))
        ToastNotification.show(self.winfo_toplevel(), "Timer durations saved.", color_theme="pink")

    def _save_user_name(self):
        name = self.ent_name.get().strip() or "Chiikawa Friend"
        database.set_setting("user_name", name)
        ToastNotification.show(self.winfo_toplevel(), f"Name updated to {name}.", color_theme="mint")

    def _reload_sample_data(self):
        database.reset_database()
        ToastNotification.show(self.winfo_toplevel(), "Sample study planner data restored.", color_theme="pink")
        self.on_reload_app()

    def _reset_all_data(self):
        database.reset_database()
        ToastNotification.show(self.winfo_toplevel(), "Planner reset to defaults.", color_theme="blue")
        self.on_reload_app()

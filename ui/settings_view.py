"""
ui/settings_view.py - Modern Settings & Preferences View for Chiikawa Study Planner
Allows users to customize visual themes (Cozy Day / Cozy Night), Pomodoro timer durations,
user profile name, sound alerts, and sample data restoration.
Refactored with PageHeader, Card, PrimaryButton, SecondaryButton, DangerButton, and StyledEntry.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Any
from theme import Theme
import database
import icons
from ui.components.widgets import (
    PageHeader,
    Card,
    PrimaryButton,
    SecondaryButton,
    DangerButton,
    StyledEntry
)
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

        # 1. Page Header
        header = PageHeader(
            self,
            title="Preferences & Settings",
            subtitle="Customize your visual theme, Pomodoro sprint lengths, and app profile."
        )
        header.pack(fill="x", padx=24, pady=(20, 14))

        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # 2. Visual Theme Settings Card
        theme_card = Card(
            scroll,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        theme_card.pack(fill="x", pady=(0, 18))

        th_inner = ctk.CTkFrame(theme_card, fg_color="transparent")
        th_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=Theme.CARD_PAD_Y)

        ctk.CTkLabel(
            th_inner,
            text="Visual Theme Mode",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            th_inner,
            text="Choose between warm alabaster Cozy Day and deep twilight Cozy Night.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 12))

        current_theme = database.get_setting("theme_mode", "light")
        self.seg_theme = ctk.CTkSegmentedButton(
            th_inner,
            values=["Cozy Day (Light)", "Cozy Night (Dark)"],
            font=Theme.font_body(),
            height=40,
            corner_radius=12,
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card_secondary"],
            unselected_hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            command=self._handle_theme_change
        )
        init_sel = "Cozy Day (Light)" if current_theme == "light" else "Cozy Night (Dark)"
        self.seg_theme.set(init_sel)
        self.seg_theme.pack(anchor="w")

        # 3. Pomodoro Timer Customization Card
        pomo_card = Card(
            scroll,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        pomo_card.pack(fill="x", pady=(0, 18))

        p_inner = ctk.CTkFrame(pomo_card, fg_color="transparent")
        p_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=Theme.CARD_PAD_Y)

        ctk.CTkLabel(
            p_inner,
            text="Pomodoro Sprint Durations (Minutes)",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            p_inner,
            text="Configure your preferred focus intervals and short / long breaks.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 14))

        inputs_grid = ctk.CTkFrame(p_inner, fg_color="transparent")
        inputs_grid.pack(fill="x", pady=(0, 16))
        inputs_grid.grid_columnconfigure((0, 1, 2), weight=1)

        f_box = ctk.CTkFrame(inputs_grid, fg_color="transparent")
        f_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(f_box, text="Focus Session (mins)", font=Theme.font_body(), text_color=colors["text_secondary"]).pack(anchor="w")
        self.ent_focus = StyledEntry(f_box, height=Theme.INPUT_HEIGHT)
        self.ent_focus.insert(0, database.get_setting("pomodoro_focus", "25"))
        self.ent_focus.pack(fill="x", pady=(4, 0))

        s_box = ctk.CTkFrame(inputs_grid, fg_color="transparent")
        s_box.grid(row=0, column=1, sticky="ew", padx=6)
        ctk.CTkLabel(s_box, text="Short Break (mins)", font=Theme.font_body(), text_color=colors["text_secondary"]).pack(anchor="w")
        self.ent_short = StyledEntry(s_box, height=Theme.INPUT_HEIGHT)
        self.ent_short.insert(0, database.get_setting("pomodoro_short_break", "5"))
        self.ent_short.pack(fill="x", pady=(4, 0))

        l_box = ctk.CTkFrame(inputs_grid, fg_color="transparent")
        l_box.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(l_box, text="Long Break (mins)", font=Theme.font_body(), text_color=colors["text_secondary"]).pack(anchor="w")
        self.ent_long = StyledEntry(l_box, height=Theme.INPUT_HEIGHT)
        self.ent_long.insert(0, database.get_setting("pomodoro_long_break", "15"))
        self.ent_long.pack(fill="x", pady=(4, 0))

        btn_save_timer = PrimaryButton(
            p_inner,
            text="Save Timer Durations",
            width=180,
            height=Theme.BTN_HEIGHT,
            command=self._save_timer_settings
        )
        btn_save_timer.pack(anchor="w")

        # 4. User Profile Name Card
        prof_card = Card(
            scroll,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        prof_card.pack(fill="x", pady=(0, 18))

        prof_inner = ctk.CTkFrame(prof_card, fg_color="transparent")
        prof_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=Theme.CARD_PAD_Y)

        ctk.CTkLabel(
            prof_inner,
            text="User Display Name",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            prof_inner,
            text="Name used for personalized greetings on your dashboard.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 12))

        name_row = ctk.CTkFrame(prof_inner, fg_color="transparent")
        name_row.pack(fill="x")

        self.ent_name = StyledEntry(
            name_row,
            placeholder_text="Your name...",
            height=Theme.INPUT_HEIGHT,
            width=240
        )
        self.ent_name.insert(0, database.get_setting("user_name", "Chiikawa Friend"))
        self.ent_name.pack(side="left", padx=(0, 12))

        btn_save_name = PrimaryButton(
            name_row,
            text="Update Name",
            width=130,
            height=Theme.BTN_HEIGHT,
            command=self._save_user_name
        )
        btn_save_name.pack(side="left")

        # 5. Data Tools & Reset Card
        data_card = Card(
            scroll,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        data_card.pack(fill="x", pady=(0, 18))

        d_inner = ctk.CTkFrame(data_card, fg_color="transparent")
        d_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=Theme.CARD_PAD_Y)

        ctk.CTkLabel(
            d_inner,
            text="Database Management & Sample Data",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            d_inner,
            text="Reload default sample subjects, tasks, and notes, or reset local database.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 14))

        btn_row = ctk.CTkFrame(d_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_reload_sample = SecondaryButton(
            btn_row,
            text="Reload Sample Data",
            height=Theme.BTN_HEIGHT,
            width=170,
            command=self._reload_sample_data
        )
        btn_reload_sample.pack(side="left", padx=(0, 12))

        btn_reset_all = DangerButton(
            btn_row,
            text="Reset to Defaults",
            height=Theme.BTN_HEIGHT,
            width=150,
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

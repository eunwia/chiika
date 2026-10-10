"""
ui/sidebar.py - Modern Minimalist Sidebar for Chiikawa Study Planner
Replaces emojis with crisp vector-styled icons, active accent indicators,
and supports full dark mode transitions.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Dict
from theme import Theme
import assets_mgr
import icons


class Sidebar(ctk.CTkFrame):
    """Left navigation sidebar with clean icons, active state indicators, and complete dark mode support."""

    NAV_ITEMS = [
        ("dashboard", "Dashboard", "dashboard"),
        ("todo", "Tasks", "tasks"),
        ("corkboard", "Corkboard", "corkboard"),
        ("calendar", "Calendar", "calendar"),
        ("study_planner", "Study Planner", "study"),
        ("pomodoro", "Focus Timer", "timer"),
        ("habits", "Habits", "habits"),
        ("notes", "Notes", "notes"),
        ("progress", "Analytics", "progress"),
        ("search", "Search", "search"),
        ("settings", "Settings", "settings"),
    ]

    def __init__(self, parent, on_navigate: Callable[[str], None], active_tab: str = "dashboard"):
        super().__init__(
            parent,
            fg_color=(Theme.LIGHT["bg_sidebar"], Theme.DARK["bg_sidebar"]),
            corner_radius=0,
            width=220,
            border_width=1,
            border_color=(Theme.LIGHT["border"], Theme.DARK["border"])
        )
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.active_tab = active_tab
        self.buttons: Dict[str, ctk.CTkButton] = {}

        self._build_ui()

    def _build_ui(self):
        colors = Theme.current()

        # Header Frame with Chiikawa Logo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(18, 10), padx=14)

        logo_img = assets_mgr.get_logo(width=140, height=36)
        if logo_img:
            self.lbl_logo = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
            self.lbl_logo.pack(anchor="w", padx=6)
        else:
            self.lbl_logo = ctk.CTkLabel(
                self.header_frame,
                text="CHIIKAWA",
                font=Theme.font_logo(),
                text_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
            )
            self.lbl_logo.pack(anchor="w", padx=6)

        self.lbl_sub = ctk.CTkLabel(
            self.header_frame,
            text="Study & Life Planner",
            font=Theme.font_tag(),
            text_color=(Theme.LIGHT["text_secondary"], Theme.DARK["text_secondary"])
        )
        self.lbl_sub.pack(anchor="w", padx=8, pady=(2, 0))

        # Thin divider
        self.divider = ctk.CTkFrame(
            self,
            fg_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            height=1
        )
        self.divider.pack(fill="x", padx=14, pady=(8, 10))

        # Scrollable Nav Container
        self.nav_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.nav_container.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        for tab_id, label, icon_name in self.NAV_ITEMS:
            is_active = (tab_id == self.active_tab)
            icon_color = colors["accent_pink"] if is_active else colors["text_secondary"]
            ic = icons.get_icon(icon_name, size=16, color=icon_color)

            btn = ctk.CTkButton(
                self.nav_container,
                text=f"  {label}",
                image=ic,
                compound="left",
                anchor="w",
                font=Theme.font_body_bold() if is_active else Theme.font_body(),
                fg_color=colors["bg_sidebar_active"] if is_active else "transparent",
                text_color=colors["accent_pink"] if is_active else colors["text_primary"],
                hover_color=colors["bg_sidebar_hover"],
                height=36,
                corner_radius=9,
                command=lambda t=tab_id: self._handle_click(t)
            )
            btn.pack(fill="x", pady=2, padx=4)
            self.buttons[tab_id] = btn

        # Bottom Mascot Motivation Widget
        self.mascot_frame = ctk.CTkFrame(
            self,
            fg_color=(Theme.LIGHT["bg_card"], Theme.DARK["bg_card"]),
            corner_radius=12,
            border_width=1,
            border_color=(Theme.LIGHT["border"], Theme.DARK["border"])
        )
        self.mascot_frame.pack(fill="x", padx=12, pady=(0, 14), side="bottom")

        m_inner = ctk.CTkFrame(self.mascot_frame, fg_color="transparent")
        m_inner.pack(padx=10, pady=8, fill="x")

        mascot_img = assets_mgr.get_illustration("hya", size=(42, 42))
        if mascot_img:
            self.lbl_mascot_img = ctk.CTkLabel(m_inner, image=mascot_img, text="")
            self.lbl_mascot_img.pack(side="left", padx=(0, 8))

        text_box = ctk.CTkFrame(m_inner, fg_color="transparent")
        text_box.pack(side="left", fill="both", expand=True)

        self.lbl_mascot_title = ctk.CTkLabel(
            text_box,
            text="Chiikawa Cheer",
            font=Theme.font_tag(),
            text_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"]),
            anchor="w"
        )
        self.lbl_mascot_title.pack(fill="x")

        self.lbl_mascot_sub = ctk.CTkLabel(
            text_box,
            text="Keep doing your best!",
            font=Theme.font_small(),
            text_color=(Theme.LIGHT["text_secondary"], Theme.DARK["text_secondary"]),
            anchor="w"
        )
        self.lbl_mascot_sub.pack(fill="x")

    def _handle_click(self, tab_id: str):
        self.set_active(tab_id)
        self.on_navigate(tab_id)

    def set_active(self, tab_id: str):
        self.active_tab = tab_id
        colors = Theme.current()
        for t, label, icon_name in self.NAV_ITEMS:
            btn = self.buttons.get(t)
            if not btn:
                continue
            if t == tab_id:
                ic = icons.get_icon(icon_name, size=16, color=colors["accent_pink"])
                btn.configure(
                    image=ic,
                    fg_color=colors["bg_sidebar_active"],
                    text_color=colors["accent_pink"],
                    font=Theme.font_body_bold()
                )
            else:
                ic = icons.get_icon(icon_name, size=16, color=colors["text_secondary"])
                btn.configure(
                    image=ic,
                    fg_color="transparent",
                    text_color=colors["text_primary"],
                    font=Theme.font_body()
                )

    def update_theme(self):
        """Called when dark/light mode is toggled to update sidebar colors and icons."""
        colors = Theme.current()
        self.configure(
            fg_color=colors["bg_sidebar"],
            border_color=colors["border"]
        )
        self.divider.configure(fg_color=colors["border_subtle"])
        self.lbl_sub.configure(text_color=colors["text_secondary"])

        self.mascot_frame.configure(
            fg_color=colors["bg_card"],
            border_color=colors["border"]
        )
        self.lbl_mascot_title.configure(text_color=colors["accent_pink"])
        self.lbl_mascot_sub.configure(text_color=colors["text_secondary"])

        # Re-apply active / inactive button colors and icons with current theme colors
        for t, label, icon_name in self.NAV_ITEMS:
            btn = self.buttons.get(t)
            if not btn:
                continue
            is_active = (t == self.active_tab)
            if is_active:
                ic = icons.get_icon(icon_name, size=16, color=colors["accent_pink"])
                btn.configure(
                    image=ic,
                    fg_color=colors["bg_sidebar_active"],
                    text_color=colors["accent_pink"],
                    hover_color=colors["bg_sidebar_hover"],
                    font=Theme.font_body_bold()
                )
            else:
                ic = icons.get_icon(icon_name, size=16, color=colors["text_secondary"])
                btn.configure(
                    image=ic,
                    fg_color="transparent",
                    text_color=colors["text_primary"],
                    hover_color=colors["bg_sidebar_hover"],
                    font=Theme.font_body()
                )

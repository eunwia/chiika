"""
ui/sidebar.py - Modern Minimalist Sidebar for Chiikawa Study Planner
Features larger 20px vector icons, 14-15px typography, clear active-tab pill highlight,
smooth hover states, built-in Dark Mode toggle, and cheerful mascot motivation widget.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Dict, Optional
from theme import Theme
import assets_mgr
import icons
from ui.components.widgets import SidebarItem


class Sidebar(ctk.CTkFrame):
    """Modern navigation sidebar with clear active-tab indicators and dark mode toggle."""

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

    def __init__(
        self,
        parent,
        on_navigate: Callable[[str], None],
        on_toggle_theme: Optional[Callable[[str], None]] = None,
        active_tab: str = "dashboard"
    ):
        super().__init__(
            parent,
            fg_color=(Theme.LIGHT["bg_sidebar"], Theme.DARK["bg_sidebar"]),
            corner_radius=0,
            width=Theme.SIDEBAR_WIDTH,
            border_width=1,
            border_color=(Theme.LIGHT["border"], Theme.DARK["border"])
        )
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.on_toggle_theme = on_toggle_theme
        self.active_tab = active_tab
        self.nav_items: Dict[str, SidebarItem] = {}

        self._build_ui()

    def _build_ui(self):
        colors = Theme.current()

        # 1. Header Frame with Chiikawa Logo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(20, 10), padx=16)

        logo_img = assets_mgr.get_logo(width=150, height=38)
        if logo_img:
            self.lbl_logo = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
            self.lbl_logo.pack(anchor="w", padx=4)
        else:
            self.lbl_logo = ctk.CTkLabel(
                self.header_frame,
                text="CHIIKAWA",
                font=Theme.font_logo(),
                text_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
            )
            self.lbl_logo.pack(anchor="w", padx=4)

        self.lbl_sub = ctk.CTkLabel(
            self.header_frame,
            text="Study & Life Planner",
            font=Theme.font_tag(),
            text_color=(Theme.LIGHT["text_secondary"], Theme.DARK["text_secondary"])
        )
        self.lbl_sub.pack(anchor="w", padx=6, pady=(3, 0))

        # Hairline divider
        self.divider = ctk.CTkFrame(
            self,
            fg_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            height=1
        )
        self.divider.pack(fill="x", padx=16, pady=(10, 8))

        # 2. Scrollable Navigation List Container
        self.nav_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.nav_container.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        for tab_id, label, icon_name in self.NAV_ITEMS:
            is_active = (tab_id == self.active_tab)
            item = SidebarItem(
                self.nav_container,
                tab_id=tab_id,
                label=label,
                icon_name=icon_name,
                command=self._handle_click,
                is_active=is_active
            )
            item.pack(fill="x", pady=2, padx=2)
            self.nav_items[tab_id] = item

        # 3. Bottom Footer Container (Pinned at bottom)
        self.footer_container = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_container.pack(fill="x", side="bottom", padx=14, pady=(0, 16))

        # Dark Mode Quick Toggle Switch Card
        self.theme_card = ctk.CTkFrame(
            self.footer_container,
            fg_color=(Theme.LIGHT["bg_card"], Theme.DARK["bg_card"]),
            corner_radius=12,
            border_width=1,
            border_color=(Theme.LIGHT["border"], Theme.DARK["border"])
        )
        self.theme_card.pack(fill="x", pady=(0, 10))

        th_inner = ctk.CTkFrame(self.theme_card, fg_color="transparent")
        th_inner.pack(padx=12, pady=8, fill="x")

        is_dark = (Theme.MODE == "dark")
        ic_theme = icons.get_icon("moon" if is_dark else "sun", size=16, color=colors["accent_yellow" if not is_dark else "accent_lavender"])
        self.lbl_theme_icon = ctk.CTkLabel(th_inner, text="", image=ic_theme)
        self.lbl_theme_icon.pack(side="left", padx=(0, 8))

        self.lbl_theme_text = ctk.CTkLabel(
            th_inner,
            text="Dark Mode" if is_dark else "Light Mode",
            font=Theme.font_body(),
            text_color=colors["text_primary"]
        )
        self.lbl_theme_text.pack(side="left")

        self.switch_theme = ctk.CTkSwitch(
            th_inner,
            text="",
            width=42,
            switch_width=38,
            switch_height=20,
            progress_color=colors["accent_pink"],
            command=self._toggle_theme
        )
        self.switch_theme.pack(side="right")
        if is_dark:
            self.switch_theme.select()
        else:
            self.switch_theme.deselect()

        # Mascot Motivation Widget
        self.mascot_frame = ctk.CTkFrame(
            self.footer_container,
            fg_color=(Theme.LIGHT["bg_card_secondary"], Theme.DARK["bg_card_secondary"]),
            corner_radius=12,
            border_width=1,
            border_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"])
        )
        self.mascot_frame.pack(fill="x")

        m_inner = ctk.CTkFrame(self.mascot_frame, fg_color="transparent")
        m_inner.pack(padx=10, pady=8, fill="x")

        mascot_img = assets_mgr.get_illustration("hya", size=(38, 38))
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

    def _toggle_theme(self):
        new_mode = "dark" if self.switch_theme.get() == 1 else "light"
        if self.on_toggle_theme:
            self.on_toggle_theme(new_mode)
        else:
            top = self.winfo_toplevel()
            if hasattr(top, "_change_theme"):
                top._change_theme(new_mode)

    def set_active(self, tab_id: str):
        self.active_tab = tab_id
        for t, item in self.nav_items.items():
            item.set_active(t == tab_id)

    def update_theme(self):
        """Called when dark/light mode is toggled to re-render colors and icons."""
        colors = Theme.current()
        self.configure(
            fg_color=colors["bg_sidebar"],
            border_color=colors["border"]
        )
        self.divider.configure(fg_color=colors["border_subtle"])
        self.lbl_sub.configure(text_color=colors["text_secondary"])

        is_dark = (Theme.MODE == "dark")
        ic_theme = icons.get_icon("moon" if is_dark else "sun", size=16, color=colors["accent_yellow" if not is_dark else "accent_lavender"])
        self.lbl_theme_icon.configure(image=ic_theme)
        self.lbl_theme_text.configure(
            text="Dark Mode" if is_dark else "Light Mode",
            text_color=colors["text_primary"]
        )
        self.theme_card.configure(
            fg_color=colors["bg_card"],
            border_color=colors["border"]
        )
        if is_dark:
            self.switch_theme.select()
        else:
            self.switch_theme.deselect()

        self.mascot_frame.configure(
            fg_color=colors["bg_card_secondary"],
            border_color=colors["border_subtle"]
        )
        self.lbl_mascot_title.configure(text_color=colors["accent_pink"])
        self.lbl_mascot_sub.configure(text_color=colors["text_secondary"])

        for item in self.nav_items.values():
            item.refresh_theme()

"""
ui/components/toast.py - In-app notification toast alerts for Chiikawa Study Planner
Displays clean, subtle, non-blocking toast banners at the bottom right.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Any, Optional
from theme import Theme
import icons


class ToastNotification:
    """Displays a transient clean toast banner in the bottom-right corner."""

    @staticmethod
    def show(parent: Any, message: str, icon_name: Optional[str] = "check", duration_ms: int = 3200, color_theme: str = "pink"):
        colors = Theme.current()
        bg_color = colors["accent_pink"]
        text_color = "#FFFFFF"

        if color_theme == "blue":
            bg_color = colors["accent_blue"]
        elif color_theme == "mint":
            bg_color = colors["accent_mint"]
        elif color_theme == "yellow":
            bg_color = colors["accent_yellow"]

        toast = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=12,
            border_width=0
        )

        content = ctk.CTkFrame(toast, fg_color="transparent")
        content.pack(padx=16, pady=10)

        if icon_name:
            ic = icons.get_icon(icon_name, size=15, color=text_color)
            lbl_icon = ctk.CTkLabel(content, image=ic, text="")
            lbl_icon.pack(side="left", padx=(0, 8))

        lbl_text = ctk.CTkLabel(
            content,
            text=message,
            font=Theme.font_body_bold(),
            text_color=text_color,
            wraplength=350,
            justify="left"
        )
        lbl_text.pack(side="left")

        toast.place(relx=0.98, rely=0.95, anchor="se")

        def fade_out():
            try:
                toast.destroy()
            except Exception:
                pass

        parent.after(duration_ms, fade_out)

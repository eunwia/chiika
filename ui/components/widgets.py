"""
ui/components/widgets.py - Modern Reusable Component Library for Chiikawa Study Planner
Provides pre-styled, consistent CustomTkinter components:
- Card, StatCard
- PrimaryButton, SecondaryButton, GhostButton, DangerButton
- SidebarItem
- StyledEntry, StyledCheckBox, StyledProgressBar
- EmptyState, PageHeader
"""

import tkinter as tk
import customtkinter as ctk
from typing import Optional, Callable, Any, Tuple, Union
from theme import Theme
import icons
import assets_mgr


class Card(ctk.CTkFrame):
    """
    Modern elevated card container with soft borders, rounded corners (16px),
    and subtle interactive hover depth.
    """
    def __init__(
        self,
        parent: Any,
        corner_radius: int = Theme.RADIUS_LG,
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_width: int = 1,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        hoverable: bool = False,
        **kwargs
    ):
        colors = Theme.current()
        if fg_color is None:
            fg_color = (Theme.LIGHT["bg_card"], Theme.DARK["bg_card"])
        if border_color is None:
            border_color = (Theme.LIGHT["border"], Theme.DARK["border"])

        super().__init__(
            parent,
            corner_radius=corner_radius,
            fg_color=fg_color,
            border_width=border_width,
            border_color=border_color,
            **kwargs
        )
        self.hoverable = hoverable
        if hoverable:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        if self.hoverable:
            colors = Theme.current()
            self.configure(border_color=colors["border_focus"])

    def _on_leave(self, event=None):
        if self.hoverable:
            colors = Theme.current()
            self.configure(border_color=colors["border"])


class PrimaryButton(ctk.CTkButton):
    """
    Eye-catching primary action button with min height 42px, rounded corners (12px),
    warm pastel rose pink fill, hover & pressed states, and crisp typography.
    """
    def __init__(
        self,
        parent: Any,
        text: str = "",
        command: Optional[Callable] = None,
        image: Optional[Any] = None,
        height: int = Theme.BTN_HEIGHT,
        width: int = 140,
        corner_radius: int = Theme.RADIUS_MD,
        **kwargs
    ):
        fg_col = kwargs.pop("fg_color", (Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"]))
        hover_col = kwargs.pop("hover_color", (Theme.LIGHT["accent_pink_hover"], Theme.DARK["accent_pink_hover"]))
        txt_col = kwargs.pop("text_color", "#FFFFFF")
        super().__init__(
            parent,
            text=text,
            command=command,
            image=image,
            compound="left" if image else "none",
            height=height,
            width=width,
            corner_radius=corner_radius,
            font=Theme.font_body_bold(),
            fg_color=fg_col,
            hover_color=hover_col,
            text_color=txt_col,
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """
    Subtle secondary button with soft neutral surface, hairline border,
    and rounded corners (12px).
    """
    def __init__(
        self,
        parent: Any,
        text: str = "",
        command: Optional[Callable] = None,
        image: Optional[Any] = None,
        height: int = Theme.BTN_HEIGHT,
        width: int = 120,
        corner_radius: int = Theme.RADIUS_MD,
        **kwargs
    ):
        fg_col = kwargs.pop("fg_color", (Theme.LIGHT["bg_card_secondary"], Theme.DARK["bg_card_secondary"]))
        hover_col = kwargs.pop("hover_color", (Theme.LIGHT["bg_sidebar_hover"], Theme.DARK["bg_sidebar_hover"]))
        border_col = kwargs.pop("border_color", (Theme.LIGHT["border"], Theme.DARK["border"]))
        txt_col = kwargs.pop("text_color", (Theme.LIGHT["text_primary"], Theme.DARK["text_primary"]))
        super().__init__(
            parent,
            text=text,
            command=command,
            image=image,
            compound="left" if image else "none",
            height=height,
            width=width,
            corner_radius=corner_radius,
            font=Theme.font_body_bold(),
            fg_color=fg_col,
            hover_color=hover_col,
            border_width=1,
            border_color=border_col,
            text_color=txt_col,
            **kwargs
        )


class GhostButton(ctk.CTkButton):
    """
    Transparent ghost button with smooth hover highlight and minimal footprint.
    """
    def __init__(
        self,
        parent: Any,
        text: str = "",
        command: Optional[Callable] = None,
        image: Optional[Any] = None,
        height: int = Theme.BTN_HEIGHT,
        width: int = 100,
        corner_radius: int = Theme.RADIUS_MD,
        text_color: Optional[Any] = None,
        **kwargs
    ):
        fg_col = kwargs.pop("fg_color", "transparent")
        hover_col = kwargs.pop("hover_color", (Theme.LIGHT["bg_card_secondary"], Theme.DARK["bg_card_secondary"]))
        txt_col = kwargs.pop("text_color", text_color or (Theme.LIGHT["text_primary"], Theme.DARK["text_primary"]))
        super().__init__(
            parent,
            text=text,
            command=command,
            image=image,
            compound="left" if image else "none",
            height=height,
            width=width,
            corner_radius=corner_radius,
            font=Theme.font_body_bold(),
            fg_color=fg_col,
            hover_color=hover_col,
            text_color=txt_col,
            **kwargs
        )


class DangerButton(ctk.CTkButton):
    """
    Destructive action button with soft coral/red styling.
    """
    def __init__(
        self,
        parent: Any,
        text: str = "",
        command: Optional[Callable] = None,
        image: Optional[Any] = None,
        height: int = Theme.BTN_HEIGHT,
        width: int = 110,
        corner_radius: int = Theme.RADIUS_MD,
        **kwargs
    ):
        fg_col = kwargs.pop("fg_color", (Theme.LIGHT["priority_high_bg"], Theme.DARK["priority_high_bg"]))
        hover_col = kwargs.pop("hover_color", (Theme.LIGHT["accent_pink_hover"], Theme.DARK["accent_pink_hover"]))
        border_col = kwargs.pop("border_color", (Theme.LIGHT["priority_high_fg"], Theme.DARK["priority_high_fg"]))
        txt_col = kwargs.pop("text_color", (Theme.LIGHT["priority_high_fg"], Theme.DARK["priority_high_fg"]))
        super().__init__(
            parent,
            text=text,
            command=command,
            image=image,
            compound="left" if image else "none",
            height=height,
            width=width,
            corner_radius=corner_radius,
            font=Theme.font_body_bold(),
            fg_color=fg_col,
            hover_color=hover_col,
            border_width=1,
            border_color=border_col,
            text_color=txt_col,
            **kwargs
        )


class SidebarItem(ctk.CTkButton):
    """
    Spacious sidebar navigation button with 20px vector icons, 15px font labels,
    active-tab highlight pill, and smooth hover feedback.
    """
    def __init__(
        self,
        parent: Any,
        tab_id: str,
        label: str,
        icon_name: str,
        command: Callable[[str], None],
        is_active: bool = False
    ):
        self.tab_id = tab_id
        self.label = label
        self.icon_name = icon_name
        self.callback = command
        self._is_active = is_active

        colors = Theme.current()
        ic = icons.get_icon(icon_name, size=20, color=colors["accent_pink"] if is_active else colors["text_secondary"])

        super().__init__(
            parent,
            text=f"   {label}",
            image=ic,
            compound="left",
            anchor="w",
            height=44,
            corner_radius=12,
            font=Theme.font_body_bold() if is_active else Theme.font_body(),
            fg_color=colors["bg_sidebar_active"] if is_active else "transparent",
            text_color=colors["accent_pink"] if is_active else colors["text_primary"],
            hover_color=colors["bg_sidebar_hover"],
            command=lambda t=tab_id, cb=command: cb(t)
        )

    def set_active(self, active: bool):
        self._is_active = active
        colors = Theme.current()
        ic = icons.get_icon(self.icon_name, size=20, color=colors["accent_pink"] if active else colors["text_secondary"])
        self.configure(
            image=ic,
            fg_color=colors["bg_sidebar_active"] if active else "transparent",
            text_color=colors["accent_pink"] if active else colors["text_primary"],
            font=Theme.font_body_bold() if active else Theme.font_body()
        )

    def refresh_theme(self):
        self.set_active(self._is_active)


class StatCard(ctk.CTkFrame):
    """
    Prominent key-metric card with colored badge icon, category title (13px),
    bold stat number (26px), and smooth rounded progress bar (8px).
    """
    def __init__(
        self,
        parent: Any,
        title: str,
        value: str,
        accent_color: str,
        icon_name: str = "tasks",
        progress: float = 0.0,
        **kwargs
    ):
        colors = Theme.current()
        super().__init__(
            parent,
            fg_color=(Theme.LIGHT["bg_card"], Theme.DARK["bg_card"]),
            corner_radius=Theme.RADIUS_LG,
            border_width=1,
            border_color=(Theme.LIGHT["border"], Theme.DARK["border"]),
            **kwargs
        )
        self.accent_color = accent_color

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=Theme.CARD_PAD_Y)

        # Top row: Title and Icon badge
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        self.lbl_title = ctk.CTkLabel(
            top_row,
            text=title,
            font=Theme.font_small(),
            text_color=colors["text_secondary"],
            anchor="w"
        )
        self.lbl_title.pack(side="left")

        # Icon pill badge
        ic = icons.get_icon(icon_name, size=15, color=accent_color)
        self.badge = ctk.CTkLabel(
            top_row,
            text="",
            image=ic,
            width=28,
            height=28,
            fg_color=colors["bg_card_secondary"],
            corner_radius=8
        )
        self.badge.pack(side="right")

        # Metric Value
        self.lbl_value = ctk.CTkLabel(
            inner,
            text=value,
            font=Theme.font_metric(),
            text_color=colors["text_primary"],
            anchor="w"
        )
        self.lbl_value.pack(anchor="w", pady=(6, 8))

        # Modern thick progress bar
        self.bar = ctk.CTkProgressBar(
            inner,
            height=8,
            corner_radius=4,
            fg_color=colors["bg_card_secondary"],
            progress_color=accent_color
        )
        self.bar.pack(fill="x")
        self.bar.set(max(0.0, min(1.0, progress)))

    def update_stat(self, value: str, progress: Optional[float] = None):
        self.lbl_value.configure(text=value)
        if progress is not None:
            self.bar.set(max(0.0, min(1.0, progress)))


class StyledEntry(ctk.CTkEntry):
    """
    Modern form input field with min height 42px, rounded corners (10px),
    generous padding, and focus highlight glow ring.
    """
    def __init__(
        self,
        parent: Any,
        placeholder_text: str = "",
        height: int = Theme.INPUT_HEIGHT,
        width: int = 240,
        corner_radius: int = 10,
        **kwargs
    ):
        colors = Theme.current()
        super().__init__(
            parent,
            placeholder_text=placeholder_text,
            height=height,
            width=width,
            corner_radius=corner_radius,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1,
            **kwargs
        )
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event=None):
        colors = Theme.current()
        self.configure(border_color=colors["border_focus"], border_width=2)

    def _on_focus_out(self, event=None):
        colors = Theme.current()
        self.configure(border_color=colors["input_border"], border_width=1)


class StyledCheckBox(ctk.CTkCheckBox):
    """
    Enlarged modern checkbox with rounded corners (6px) and Chiikawa rose pink fill.
    """
    def __init__(
        self,
        parent: Any,
        text: str = "",
        command: Optional[Callable] = None,
        variable: Optional[Any] = None,
        **kwargs
    ):
        colors = Theme.current()
        super().__init__(
            parent,
            text=text,
            command=command,
            variable=variable,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=6,
            font=Theme.font_body(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            border_color=colors["border"],
            border_width=1,
            text_color=colors["text_primary"],
            **kwargs
        )


class StyledProgressBar(ctk.CTkProgressBar):
    """
    Substantial, smooth rounded progress bar (8px height).
    """
    def __init__(
        self,
        parent: Any,
        height: int = 8,
        corner_radius: int = 4,
        progress_color: Optional[str] = None,
        **kwargs
    ):
        colors = Theme.current()
        super().__init__(
            parent,
            height=height,
            corner_radius=corner_radius,
            fg_color=colors["bg_card_secondary"],
            progress_color=progress_color or colors["accent_pink"],
            **kwargs
        )


class PageHeader(ctk.CTkFrame):
    """
    Standard modern page header with bold 28px title, 14px description,
    and right-side action button container.
    """
    def __init__(
        self,
        parent: Any,
        title: str,
        subtitle: str = "",
        **kwargs
    ):
        kwargs.setdefault("height", 0)
        super().__init__(parent, fg_color="transparent", **kwargs)
        colors = Theme.current()

        text_container = ctk.CTkFrame(self, fg_color="transparent", height=0)
        text_container.pack(side="left", fill="both", expand=True)

        self.lbl_title = ctk.CTkLabel(
            text_container,
            text=title,
            font=Theme.font_page_title(),
            text_color=colors["text_primary"],
            anchor="w"
        )
        self.lbl_title.pack(anchor="w")

        if subtitle:
            self.lbl_subtitle = ctk.CTkLabel(
                text_container,
                text=subtitle,
                font=Theme.font_body(),
                text_color=colors["text_secondary"],
                anchor="w"
            )
            self.lbl_subtitle.pack(anchor="w", pady=(3, 0))

        self.actions_container = ctk.CTkFrame(self, fg_color="transparent", width=0, height=0)
        self.actions_container.pack(side="right", fill="y", padx=(16, 0))


class EmptyState(ctk.CTkFrame):
    """
    Friendly illustrated empty state card with Chiikawa mascot,
    clean messaging, and optional primary call to action.
    """
    def __init__(
        self,
        parent: Any,
        title: str = "Nothing here yet!",
        description: str = "Chiikawa is cheering for you. Get started whenever you're ready!",
        mascot_name: str = "passed",
        action_text: Optional[str] = None,
        action_command: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        colors = Theme.current()

        img = assets_mgr.get_illustration(mascot_name, size=(80, 80))
        if img:
            self.lbl_img = ctk.CTkLabel(self, image=img, text="")
            self.lbl_img.pack(pady=(12, 8))

        self.lbl_title = ctk.CTkLabel(
            self,
            text=title,
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        )
        self.lbl_title.pack(pady=(0, 4))

        self.lbl_desc = ctk.CTkLabel(
            self,
            text=description,
            font=Theme.font_body(),
            text_color=colors["text_secondary"],
            justify="center"
        )
        self.lbl_desc.pack(pady=(0, 16))

        if action_text and action_command:
            self.btn_action = PrimaryButton(
                self,
                text=action_text,
                command=action_command,
                width=160
            )
            self.btn_action.pack()

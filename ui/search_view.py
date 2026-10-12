"""
ui/search_view.py - Modern Universal Search & Multi-Filter View for Chiikawa Study Planner
Searches across tasks, notes, calendar events, and courses with multi-attribute filtering.
Refactored with PageHeader, Card, SecondaryButton, StyledEntry, and EmptyState.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Optional, Any, List, Dict
from theme import Theme
import database
import icons
from ui.components.widgets import (
    PageHeader,
    Card,
    SecondaryButton,
    StyledEntry,
    EmptyState
)
from ui.components.toast import ToastNotification


class SearchView(ctk.CTkFrame):
    """Universal search and filtering engine across all planner entities."""

    def __init__(self, parent: Any, on_navigate: Optional[Any] = None):
        super().__init__(parent, fg_color="transparent")
        self.on_navigate = on_navigate
        self.search_query = ""

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        # 1. Page Header
        header = PageHeader(
            self,
            title="Universal Search",
            subtitle="Locate tasks, notes, courses, and calendar events instantly across your entire planner."
        )
        header.pack(fill="x", padx=24, pady=(20, 20))

        # 2. Filter & Search Card
        filter_card = Card(
            self,
            corner_radius=Theme.RADIUS_MD,
            hoverable=False
        )
        filter_card.pack(fill="x", padx=24, pady=(0, 14))

        f_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        f_inner.pack(fill="x", padx=16, pady=14)

        search_line = ctk.CTkFrame(f_inner, fg_color="transparent")
        search_line.pack(fill="x", pady=(0, 12))

        self.ent_search = StyledEntry(
            search_line,
            placeholder_text="Type search keywords (e.g. Calculus, Chapter, Review, Exam)...",
            height=Theme.INPUT_HEIGHT
        )
        self.ent_search.configure(font=Theme.font_card_title())
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_search.bind("<KeyRelease>", lambda e: self._on_search_change())

        btn_clear = SecondaryButton(
            search_line,
            text="Clear",
            width=80,
            height=Theme.BTN_HEIGHT,
            command=self._clear_search
        )
        btn_clear.pack(side="right")

        filter_row = ctk.CTkFrame(f_inner, fg_color="transparent")
        filter_row.pack(fill="x")

        ctk.CTkLabel(
            filter_row,
            text="Scope:",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="left", padx=(0, 6))

        self.opt_scope = ctk.CTkOptionMenu(
            filter_row,
            values=["All Items", "Tasks Only", "Notes Only", "Events Only"],
            font=Theme.font_body(),
            width=130,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            command=lambda v: self.refresh()
        )
        self.opt_scope.set("All Items")
        self.opt_scope.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            filter_row,
            text="Priority:",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="left", padx=(0, 6))

        self.opt_priority = ctk.CTkOptionMenu(
            filter_row,
            values=["All", "High", "Medium", "Low"],
            font=Theme.font_body(),
            width=110,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            command=lambda v: self.refresh()
        )
        self.opt_priority.set("All")
        self.opt_priority.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            filter_row,
            text="Status:",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="left", padx=(0, 6))

        self.opt_status = ctk.CTkOptionMenu(
            filter_row,
            values=["All", "Active", "Completed"],
            font=Theme.font_body(),
            width=115,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            command=lambda v: self.refresh()
        )
        self.opt_status.set("All")
        self.opt_status.pack(side="left")

        self.lbl_result_count = ctk.CTkLabel(
            filter_row,
            text="",
            font=Theme.font_tag(),
            text_color=colors["accent_pink"]
        )
        self.lbl_result_count.pack(side="right")

        # 3. Results Container
        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.results_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def _on_search_change(self):
        self.search_query = self.ent_search.get().strip()
        self.refresh()

    def _clear_search(self):
        self.ent_search.delete(0, "end")
        self.search_query = ""
        self.refresh()

    def refresh(self):
        colors = Theme.current()
        for child in self.results_scroll.winfo_children():
            child.destroy()

        scope = self.opt_scope.get()
        prio = self.opt_priority.get()
        stat = self.opt_status.get().lower()
        q = self.search_query

        matched_tasks = []
        matched_notes = []
        matched_events = []

        if scope in ("All Items", "Tasks Only"):
            matched_tasks = database.get_tasks(
                filter_status=stat,
                priority=prio if prio != "All" else None,
                search_query=q or None
            )

        if scope in ("All Items", "Notes Only"):
            matched_notes = database.get_notes(search_query=q or None)

        if scope in ("All Items", "Events Only"):
            all_ev = database.get_calendar_events()
            if q:
                matched_events = [e for e in all_ev if q.lower() in e["title"].lower() or q.lower() in e.get("notes", "").lower()]
            else:
                matched_events = all_ev

        total_matches = len(matched_tasks) + len(matched_notes) + len(matched_events)
        self.lbl_result_count.configure(text=f"{total_matches} items found")

        if total_matches == 0:
            empty = EmptyState(
                self.results_scroll,
                title="No matching items found",
                description="Try another keyword or adjust your scope and filter settings.",
                mascot_name="passed"
            )
            empty.pack(fill="x", pady=32)
            return

        if matched_tasks:
            ctk.CTkLabel(
                self.results_scroll,
                text=f"Tasks ({len(matched_tasks)})",
                font=Theme.font_card_title(),
                text_color=colors["accent_pink"]
            ).pack(anchor="w", pady=(8, 6))

            for t in matched_tasks:
                self._render_task_item(t)

        if matched_notes:
            ctk.CTkLabel(
                self.results_scroll,
                text=f"Notes ({len(matched_notes)})",
                font=Theme.font_card_title(),
                text_color=colors["accent_blue"]
            ).pack(anchor="w", pady=(18, 6))

            for n in matched_notes:
                self._render_note_item(n)

        if matched_events:
            ctk.CTkLabel(
                self.results_scroll,
                text=f"Calendar Events ({len(matched_events)})",
                font=Theme.font_card_title(),
                text_color=colors["accent_yellow"]
            ).pack(anchor="w", pady=(18, 6))

            for ev in matched_events:
                self._render_event_item(ev)

    def _render_task_item(self, task: dict):
        colors = Theme.current()
        card = Card(
            self.results_scroll,
            corner_radius=Theme.RADIUS_MD,
            border_width=1,
            border_color=colors["border_subtle"],
            hoverable=True
        )
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        st = "✓" if task["completed"] else "○"
        ctk.CTkLabel(
            inner,
            text=f"{st}  {task['title']}",
            font=Theme.font_body_bold(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        due_txt = f"Due: {task.get('due_date', 'None')}"
        ctk.CTkLabel(
            inner,
            text=f"Priority: {task.get('priority')}  |  {due_txt}",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="right")

    def _render_note_item(self, note: dict):
        colors = Theme.current()
        card = Card(
            self.results_scroll,
            corner_radius=Theme.RADIUS_MD,
            border_width=1,
            border_color=colors["border_subtle"],
            hoverable=True
        )
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(
            inner,
            text=note['title'],
            font=Theme.font_body_bold(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        snip = note.get("content", "").replace("\n", " ")[:80]
        if snip:
            ctk.CTkLabel(
                inner,
                text=snip + "...",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(anchor="w", pady=(3, 0))

    def _render_event_item(self, ev: dict):
        colors = Theme.current()
        card = Card(
            self.results_scroll,
            corner_radius=Theme.RADIUS_MD,
            border_width=1,
            border_color=colors["border_subtle"],
            hoverable=True
        )
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(
            inner,
            text=f"[{ev.get('event_type')}] {ev['title']}",
            font=Theme.font_body_bold(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            inner,
            text=f"Date: {ev.get('start_date')} at {ev.get('start_time')}",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="right")

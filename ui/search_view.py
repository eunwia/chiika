"""
ui/search_view.py - Modern Universal Search & Multi-Filter View for Chiikawa Study Planner
Searches across tasks, notes, calendar events, and courses with multi-attribute filtering.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Optional, Any, List, Dict
from theme import Theme
import database
import icons
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

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 12))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Universal Search",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Locate tasks, notes, courses, and calendar events instantly across your entire planner.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        filter_card = ctk.CTkFrame(
            self,
            fg_color=colors["bg_card"],
            corner_radius=14,
            border_width=1,
            border_color=colors["border"]
        )
        filter_card.pack(fill="x", padx=24, pady=(0, 12))

        f_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        f_inner.pack(fill="x", padx=16, pady=12)

        search_line = ctk.CTkFrame(f_inner, fg_color="transparent")
        search_line.pack(fill="x", pady=(0, 10))

        self.ent_search = ctk.CTkEntry(
            search_line,
            placeholder_text="Type search keywords (e.g. Calculus, Chapter, Review, Exam)...",
            font=Theme.font_header(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=40
        )
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_search.bind("<KeyRelease>", lambda e: self._on_search_change())

        btn_clear = ctk.CTkButton(
            search_line,
            text="Clear",
            font=Theme.font_body(),
            width=70,
            height=40,
            fg_color=colors["bg_card_secondary"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            command=self._clear_search
        )
        btn_clear.pack(side="right")

        filter_row = ctk.CTkFrame(f_inner, fg_color="transparent")
        filter_row.pack(fill="x")

        ctk.CTkLabel(filter_row, text="Scope:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 4))
        self.opt_scope = ctk.CTkOptionMenu(
            filter_row,
            values=["All Items", "Tasks Only", "Notes Only", "Events Only"],
            font=Theme.font_small(),
            width=110,
            height=28,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            command=lambda v: self.refresh()
        )
        self.opt_scope.set("All Items")
        self.opt_scope.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filter_row, text="Priority:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 4))
        self.opt_priority = ctk.CTkOptionMenu(
            filter_row,
            values=["All", "High", "Medium", "Low"],
            font=Theme.font_small(),
            width=90,
            height=28,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            command=lambda v: self.refresh()
        )
        self.opt_priority.set("All")
        self.opt_priority.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filter_row, text="Status:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 4))
        self.opt_status = ctk.CTkOptionMenu(
            filter_row,
            values=["All", "Active", "Completed"],
            font=Theme.font_small(),
            width=95,
            height=28,
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

        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
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
            ctk.CTkLabel(
                self.results_scroll,
                text="No matching items found. Try another search keyword.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(pady=40)
            return

        if matched_tasks:
            ctk.CTkLabel(self.results_scroll, text=f"Tasks ({len(matched_tasks)})", font=Theme.font_header(), text_color=colors["accent_pink"]).pack(anchor="w", pady=(8, 4))
            for t in matched_tasks:
                self._render_task_item(t)

        if matched_notes:
            ctk.CTkLabel(self.results_scroll, text=f"Notes ({len(matched_notes)})", font=Theme.font_header(), text_color=colors["accent_blue"]).pack(anchor="w", pady=(16, 4))
            for n in matched_notes:
                self._render_note_item(n)

        if matched_events:
            ctk.CTkLabel(self.results_scroll, text=f"Calendar Events ({len(matched_events)})", font=Theme.font_header(), text_color=colors["accent_yellow"]).pack(anchor="w", pady=(16, 4))
            for ev in matched_events:
                self._render_event_item(ev)

    def _render_task_item(self, task: dict):
        colors = Theme.current()
        card = ctk.CTkFrame(self.results_scroll, fg_color=colors["bg_card"], corner_radius=10, border_width=1, border_color=colors["border_subtle"])
        card.pack(fill="x", pady=3)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=8)

        st = "✓" if task["completed"] else "○"
        ctk.CTkLabel(inner, text=f"{st}  {task['title']}", font=Theme.font_body_bold(), text_color=colors["text_primary"]).pack(side="left")

        due_txt = f"Due: {task.get('due_date', 'None')}"
        ctk.CTkLabel(inner, text=f"Priority: {task.get('priority')}  |  {due_txt}", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="right")

    def _render_note_item(self, note: dict):
        colors = Theme.current()
        card = ctk.CTkFrame(self.results_scroll, fg_color=colors["bg_card"], corner_radius=10, border_width=1, border_color=colors["border_subtle"])
        card.pack(fill="x", pady=3)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=8)

        ctk.CTkLabel(inner, text=note['title'], font=Theme.font_body_bold(), text_color=colors["text_primary"]).pack(anchor="w")
        snip = note.get("content", "").replace("\n", " ")[:80]
        if snip:
            ctk.CTkLabel(inner, text=snip + "...", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w", pady=(2, 0))

    def _render_event_item(self, ev: dict):
        colors = Theme.current()
        card = ctk.CTkFrame(self.results_scroll, fg_color=colors["bg_card"], corner_radius=10, border_width=1, border_color=colors["border_subtle"])
        card.pack(fill="x", pady=3)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=8)

        ctk.CTkLabel(inner, text=f"[{ev.get('event_type')}] {ev['title']}", font=Theme.font_body_bold(), text_color=colors["text_primary"]).pack(side="left")
        ctk.CTkLabel(inner, text=f"Date: {ev.get('start_date')} at {ev.get('start_time')}", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="right")

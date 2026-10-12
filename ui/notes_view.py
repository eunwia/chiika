"""
ui/notes_view.py - Modern Notes & Quick Capture View for Chiikawa Study Planner
Master-detail notes manager with quick capture bar, rich inline editor, search, and pin controls.
Refactored with PageHeader, Card, PrimaryButton, SecondaryButton, GhostButton, StyledEntry, and StyledCheckBox.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date
from typing import Optional, Any, List
from theme import Theme
import database
import icons
from ui.components.widgets import (
    PageHeader,
    Card,
    PrimaryButton,
    SecondaryButton,
    GhostButton,
    DangerButton,
    StyledEntry,
    StyledCheckBox,
    EmptyState
)
from ui.components.modal import NoteModal
from ui.components.toast import ToastNotification


class NotesView(ctk.CTkFrame):
    """Notes and quick capture workspace with master-detail layout."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self.selected_note_id: Optional[int] = None
        self.search_term = ""

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        # 1. Page Header with Action Button
        header = PageHeader(
            self,
            title="Study Notes",
            subtitle="Capture lecture summaries, revision guides, ideas, and formulas."
        )
        header.pack(fill="x", padx=24, pady=(20, 14))

        ic_plus = icons.get_icon("plus", size=16, color="#FFFFFF")
        btn_new_note = PrimaryButton(
            header.actions_container,
            text="Create Note",
            image=ic_plus,
            command=self._open_create_note_modal,
            width=140,
            height=Theme.BTN_HEIGHT
        )
        btn_new_note.pack(side="right")

        # 2. Quick Capture Bar Card
        cap_bar = Card(
            self,
            corner_radius=Theme.RADIUS_MD,
            hoverable=False
        )
        cap_bar.pack(fill="x", padx=24, pady=(0, 14))

        cap_inner = ctk.CTkFrame(cap_bar, fg_color="transparent")
        cap_inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(
            cap_inner,
            text="Quick Capture:",
            font=Theme.font_body_bold(),
            text_color=colors["accent_pink"]
        ).pack(side="left", padx=(0, 10))

        self.ent_quick = StyledEntry(
            cap_inner,
            placeholder_text="Jot down a quick thought, formula, or reminder (Press Enter to save)...",
            height=38
        )
        self.ent_quick.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_quick.bind("<Return>", lambda e: self._handle_quick_capture())

        btn_quick_save = PrimaryButton(
            cap_inner,
            text="Save Note",
            width=110,
            height=38,
            command=self._handle_quick_capture
        )
        btn_quick_save.pack(side="left")

        # 3. Master-Detail Layout Area
        main_area = ctk.CTkFrame(self, fg_color="transparent")
        main_area.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        main_area.grid_columnconfigure(0, weight=4)
        main_area.grid_columnconfigure(1, weight=6)
        main_area.grid_rowconfigure(0, weight=1)

        # Left Column: Note List Card
        left_card = Card(
            main_area,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        search_box = ctk.CTkFrame(left_card, fg_color="transparent")
        search_box.pack(fill="x", padx=14, pady=(14, 8))

        self.ent_search = StyledEntry(
            search_box,
            placeholder_text="Search notes...",
            height=36
        )
        self.ent_search.pack(fill="x")
        self.ent_search.bind("<KeyRelease>", lambda e: self._on_search())

        self.notes_scroll = ctk.CTkScrollableFrame(
            left_card,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.notes_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        # Right Column: Editor & Viewer Card
        self.editor_card = Card(
            main_area,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        self.editor_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._build_editor()

    def _build_editor(self):
        colors = Theme.current()
        self.editor_inner = ctk.CTkFrame(self.editor_card, fg_color="transparent")
        self.editor_inner.pack(fill="both", expand=True, padx=20, pady=16)

        # Header with Title, Primary Save Button, and Delete
        top_row = ctk.CTkFrame(self.editor_inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 12))

        self.ent_title = StyledEntry(
            top_row,
            placeholder_text="Note Title...",
            height=Theme.INPUT_HEIGHT
        )
        self.ent_title.configure(font=Theme.font_card_title())
        self.ent_title.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_save_top = PrimaryButton(
            top_row,
            text="Save Note",
            height=Theme.BTN_HEIGHT,
            width=110,
            command=self._save_current_note
        )
        self.btn_save_top.pack(side="left", padx=(0, 8))

        ic_trash = icons.get_icon("trash", size=15, color=colors["priority_high_fg"])
        self.btn_del = DangerButton(
            top_row,
            text="Delete",
            image=ic_trash,
            width=88,
            height=Theme.BTN_HEIGHT,
            command=self._delete_current_note
        )
        self.btn_del.pack(side="right")

        # Metadata Row (Subject, Category, Pin)
        meta_row = ctk.CTkFrame(self.editor_inner, fg_color="transparent")
        meta_row.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            meta_row,
            text="Course:",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="left", padx=(0, 6))

        self.subjects = database.get_all_subjects()
        s_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        self.opt_subject = ctk.CTkOptionMenu(
            meta_row,
            values=s_names,
            font=Theme.font_body(),
            width=165,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"]
        )
        self.opt_subject.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            meta_row,
            text="Category:",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(side="left", padx=(0, 6))

        self.opt_category = ctk.CTkOptionMenu(
            meta_row,
            values=["General", "Lecture", "Summary", "Inspiration", "Draft", "Quick Capture"],
            font=Theme.font_body(),
            width=135,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"]
        )
        self.opt_category.pack(side="left", padx=(0, 14))

        self.var_pin = tk.BooleanVar(value=False)
        self.chk_pin = StyledCheckBox(
            meta_row,
            text="Pin Note",
            variable=self.var_pin
        )
        self.chk_pin.pack(side="left")

        # Text Area
        self.txt_content = ctk.CTkTextbox(
            self.editor_inner,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1,
            corner_radius=10
        )
        self.txt_content.pack(fill="both", expand=True, pady=(0, 12))

        # Bottom Status Bar
        ftr = ctk.CTkFrame(self.editor_inner, fg_color="transparent")
        ftr.pack(fill="x")

        self.lbl_updated = ctk.CTkLabel(
            ftr,
            text="",
            font=Theme.font_tag(),
            text_color=colors["text_muted"]
        )
        self.lbl_updated.pack(side="left")

        btn_save_bottom = PrimaryButton(
            ftr,
            text="Save Changes",
            height=36,
            width=130,
            command=self._save_current_note
        )
        btn_save_bottom.pack(side="right")

    def _on_search(self):
        self.search_term = self.ent_search.get().strip()
        self.refresh()

    def refresh(self):
        colors = Theme.current()
        for child in self.notes_scroll.winfo_children():
            child.destroy()

        notes = database.get_notes(search_query=self.search_term or None)

        if not notes:
            ctk.CTkLabel(
                self.notes_scroll,
                text="No notes found.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(pady=24)
            return

        if not self.selected_note_id or not any(n["id"] == self.selected_note_id for n in notes):
            self.selected_note_id = notes[0]["id"]

        for note in notes:
            self._render_note_list_item(note)

        sel_note = next((n for n in notes if n["id"] == self.selected_note_id), None)
        if sel_note:
            self._load_note_into_editor(sel_note)

    def _render_note_list_item(self, note: dict):
        colors = Theme.current()
        nid = note["id"]
        is_sel = (nid == self.selected_note_id)

        item = Card(
            self.notes_scroll,
            fg_color=colors["bg_sidebar_active"] if is_sel else colors["bg_card"],
            corner_radius=Theme.RADIUS_MD,
            border_width=1,
            border_color=colors["accent_pink"] if is_sel else colors["border_subtle"],
            hoverable=True
        )
        item.pack(fill="x", pady=3)

        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=10)

        top_line = ctk.CTkFrame(inner, fg_color="transparent")
        top_line.pack(fill="x")

        if note.get("pinned"):
            ic_pin = icons.get_icon("pin", size=13, color=colors["accent_pink"])
            ctk.CTkLabel(top_line, image=ic_pin, text="").pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            top_line,
            text=note["title"],
            font=Theme.font_body_bold(),
            text_color=colors["text_primary"],
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        snippet = note.get("content", "").replace("\n", " ")[:38]
        if snippet:
            ctk.CTkLabel(
                inner,
                text=snippet + ("..." if len(note.get("content", "")) > 38 else ""),
                font=Theme.font_small(),
                text_color=colors["text_secondary"],
                anchor="w"
            ).pack(fill="x", pady=(2, 4))

        meta_line = ctk.CTkFrame(inner, fg_color="transparent")
        meta_line.pack(fill="x")

        ctk.CTkLabel(
            meta_line,
            text=note.get("category", "General"),
            font=Theme.font_tag(),
            text_color=colors["text_secondary"],
            fg_color=colors["bg_card_secondary"],
            corner_radius=5,
            padx=6,
            pady=1
        ).pack(side="left")

        date_short = note.get("updated_at", "")[:10]
        ctk.CTkLabel(
            meta_line,
            text=date_short,
            font=Theme.font_small(),
            text_color=colors["text_muted"]
        ).pack(side="right")

        # Click to select
        for w in [item, inner, top_line, meta_line]:
            w.bind("<Button-1>", lambda e, n=nid: self._select_note(n))

    def _select_note(self, note_id: int):
        self.selected_note_id = note_id
        self.refresh()

    def _load_note_into_editor(self, note: dict):
        self.ent_title.delete(0, "end")
        self.ent_title.insert(0, note["title"])

        self.txt_content.delete("1.0", "end")
        self.txt_content.insert("1.0", note.get("content", ""))

        self.var_pin.set(bool(note.get("pinned", 0)))
        cat = note.get("category", "General")
        self.opt_category.set(cat)

        sid = note.get("subject_id")
        sub_name = "General (No Subject)"
        if sid:
            for s in self.subjects:
                if s["id"] == sid:
                    sub_name = s["name"]
                    break
        self.opt_subject.set(sub_name)

        up_str = note.get("updated_at", "")
        self.lbl_updated.configure(text=f"Last modified: {up_str}")

    def _save_current_note(self):
        if not self.selected_note_id:
            return

        title = self.ent_title.get().strip()
        if not title:
            ToastNotification.show(self.winfo_toplevel(), "Note title cannot be empty.", color_theme="pink")
            return

        content = self.txt_content.get("1.0", "end-1c")
        category = self.opt_category.get()
        pinned = int(self.var_pin.get())

        sel_sub_name = self.opt_subject.get()
        subject_id = None
        for s in self.subjects:
            if s["name"] == sel_sub_name:
                subject_id = s["id"]
                break

        database.update_note(
            note_id=self.selected_note_id,
            title=title,
            content=content,
            subject_id=subject_id,
            category=category,
            pinned=pinned
        )
        ToastNotification.show(self.winfo_toplevel(), "Note saved successfully.", color_theme="pink")
        self.refresh()

    def _delete_current_note(self):
        if not self.selected_note_id:
            return
        database.delete_note(self.selected_note_id)
        self.selected_note_id = None
        ToastNotification.show(self.winfo_toplevel(), "Note deleted.", color_theme="blue")
        self.refresh()

    def _handle_quick_capture(self):
        text = self.ent_quick.get().strip()
        if not text:
            return
        today_str = date.today().strftime("%b %d, %Y")
        database.add_note(
            title=f"Quick Capture ({today_str})",
            content=text,
            category="Quick Capture"
        )
        self.ent_quick.delete(0, "end")
        ToastNotification.show(self.winfo_toplevel(), "Quick note saved.", color_theme="mint")
        self.refresh()

    def _open_create_note_modal(self):
        def on_saved(data):
            nid = database.add_note(
                title=data["title"],
                content=data["content"],
                subject_id=data["subject_id"],
                category=data["category"],
                pinned=data["pinned"]
            )
            self.selected_note_id = nid
            ToastNotification.show(self.winfo_toplevel(), "Note created.", color_theme="pink")
            self.refresh()

        NoteModal(self.winfo_toplevel(), on_saved)

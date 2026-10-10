"""
ui/notes_view.py - Modern Notes & Quick Capture View for Chiikawa Study Planner
Master-detail notes manager with dedicated Create Note modal, inline editor,
guaranteed visible Save/Cancel buttons, search, and pin controls.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date
from typing import Optional, Any, List
from theme import Theme
import database
import icons
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

        # Header Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 12))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Study Notes",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Capture lecture summaries, revision guides, ideas, and formulas.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        ic_plus = icons.get_icon("plus", size=14, color="#FFFFFF")
        btn_new_note = ctk.CTkButton(
            header,
            text=" Create Note",
            image=ic_plus,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=36,
            command=self._open_create_note_modal
        )
        btn_new_note.pack(side="right")

        # Quick Capture Bar
        cap_bar = ctk.CTkFrame(
            self,
            fg_color=colors["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=colors["border"]
        )
        cap_bar.pack(fill="x", padx=24, pady=(0, 12))

        cap_inner = ctk.CTkFrame(cap_bar, fg_color="transparent")
        cap_inner.pack(fill="x", padx=14, pady=8)

        ctk.CTkLabel(cap_inner, text="Quick Capture:", font=Theme.font_subheader(), text_color=colors["accent_pink"]).pack(side="left", padx=(0, 8))

        self.ent_quick = ctk.CTkEntry(
            cap_inner,
            placeholder_text="Jot down a quick thought, formula, or reminder (Press Enter to save)...",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=32
        )
        self.ent_quick.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ent_quick.bind("<Return>", lambda e: self._handle_quick_capture())

        btn_quick_save = ctk.CTkButton(
            cap_inner,
            text="Save Note",
            font=Theme.font_small(),
            width=85,
            height=32,
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            command=self._handle_quick_capture
        )
        btn_quick_save.pack(side="left")

        # Master-Detail Layout Area
        main_area = ctk.CTkFrame(self, fg_color="transparent")
        main_area.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        main_area.grid_columnconfigure(0, weight=4)
        main_area.grid_columnconfigure(1, weight=6)
        main_area.grid_rowconfigure(0, weight=1)

        # Left Column: Note List
        left_card = ctk.CTkFrame(
            main_area,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        search_box = ctk.CTkFrame(left_card, fg_color="transparent")
        search_box.pack(fill="x", padx=14, pady=(14, 8))

        self.ent_search = ctk.CTkEntry(
            search_box,
            placeholder_text="Search notes...",
            font=Theme.font_small(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=30
        )
        self.ent_search.pack(fill="x")
        self.ent_search.bind("<KeyRelease>", lambda e: self._on_search())

        self.notes_scroll = ctk.CTkScrollableFrame(
            left_card,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
        )
        self.notes_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        # Right Column: Editor & Viewer Card
        self.editor_card = ctk.CTkFrame(
            main_area,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        self.editor_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._build_editor()

    def _build_editor(self):
        colors = Theme.current()
        self.editor_inner = ctk.CTkFrame(self.editor_card, fg_color="transparent")
        self.editor_inner.pack(fill="both", expand=True, padx=20, pady=16)

        # Header with Title, Primary Save Button, and Delete
        top_row = ctk.CTkFrame(self.editor_inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        self.ent_title = ctk.CTkEntry(
            top_row,
            placeholder_text="Note Title...",
            font=Theme.font_header(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_title.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Prominent Save Note Button at the top
        self.btn_save_top = ctk.CTkButton(
            top_row,
            text="Save Note",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=8,
            height=34,
            width=100,
            command=self._save_current_note
        )
        self.btn_save_top.pack(side="left", padx=(0, 6))

        ic_trash = icons.get_icon("trash", size=13, color="#D94161")
        self.btn_del = ctk.CTkButton(
            top_row,
            text="",
            image=ic_trash,
            width=32,
            height=34,
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            command=self._delete_current_note
        )
        self.btn_del.pack(side="right")

        # Metadata Row (Subject, Category, Pin)
        meta_row = ctk.CTkFrame(self.editor_inner, fg_color="transparent")
        meta_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(meta_row, text="Course:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 4))
        self.subjects = database.get_all_subjects()
        s_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        self.opt_subject = ctk.CTkOptionMenu(
            meta_row,
            values=s_names,
            font=Theme.font_small(),
            width=150,
            height=28,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"]
        )
        self.opt_subject.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(meta_row, text="Category:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 4))
        self.opt_category = ctk.CTkOptionMenu(
            meta_row,
            values=["General", "Lecture", "Summary", "Inspiration", "Draft", "Quick Capture"],
            font=Theme.font_small(),
            width=120,
            height=28,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"]
        )
        self.opt_category.pack(side="left", padx=(0, 12))

        self.var_pin = tk.BooleanVar(value=False)
        self.chk_pin = ctk.CTkCheckBox(
            meta_row,
            text="Pin Note",
            variable=self.var_pin,
            font=Theme.font_small(),
            text_color=colors["text_primary"],
            fg_color=colors["accent_pink"],
            border_color=colors["border"]
        )
        self.chk_pin.pack(side="left")

        # Text Area
        self.txt_content = ctk.CTkTextbox(
            self.editor_inner,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1
        )
        self.txt_content.pack(fill="both", expand=True, pady=(0, 10))

        # Bottom Status Bar with duplicate Save Note button
        ftr = ctk.CTkFrame(self.editor_inner, fg_color="transparent")
        ftr.pack(fill="x")

        self.lbl_updated = ctk.CTkLabel(
            ftr,
            text="",
            font=Theme.font_tag(),
            text_color=colors["text_muted"]
        )
        self.lbl_updated.pack(side="left")

        btn_save_bottom = ctk.CTkButton(
            ftr,
            text="Save Changes",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=8,
            height=32,
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
                font=Theme.font_small(),
                text_color=colors["text_secondary"]
            ).pack(pady=20)
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

        item = ctk.CTkFrame(
            self.notes_scroll,
            fg_color=colors["bg_sidebar_active"] if is_sel else colors["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=colors["accent_pink"] if is_sel else colors["border_subtle"]
        )
        item.pack(fill="x", pady=3)

        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=8)

        top_line = ctk.CTkFrame(inner, fg_color="transparent")
        top_line.pack(fill="x")

        if note.get("pinned"):
            ic_pin = icons.get_icon("pin", size=11, color=colors["accent_pink"])
            ctk.CTkLabel(top_line, image=ic_pin, text="").pack(side="left", padx=(0, 4))

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
                text=snippet + "...",
                font=Theme.font_small(),
                text_color=colors["text_secondary"],
                anchor="w"
            ).pack(fill="x", pady=(2, 0))

        badg_line = ctk.CTkFrame(inner, fg_color="transparent")
        badg_line.pack(fill="x", pady=(4, 0))

        sub_n = note.get("subject_name") or "General"
        ctk.CTkLabel(
            badg_line,
            text=sub_n,
            font=Theme.font_tag(),
            text_color=colors["text_secondary"],
            fg_color=colors["bg_card_secondary"],
            corner_radius=4,
            padx=5,
            pady=1
        ).pack(side="left")

        for w in [item, inner, top_line]:
            w.bind("<Button-1>", lambda e, id_val=nid: self._select_note(id_val))

    def _select_note(self, note_id: int):
        self.selected_note_id = note_id
        self.refresh()

    def _load_note_into_editor(self, note: dict):
        self.ent_title.delete(0, "end")
        self.ent_title.insert(0, note["title"])

        self.txt_content.delete("1.0", "end")
        self.txt_content.insert("1.0", note.get("content", ""))

        self.var_pin.set(bool(note.get("pinned")))

        sub_name = note.get("subject_name") or "General (No Subject)"
        s_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        if sub_name in s_names:
            self.opt_subject.set(sub_name)
        else:
            self.opt_subject.set("General (No Subject)")

        self.opt_category.set(note.get("category", "General"))
        updated_at = note.get("updated_at", "")[:16].replace("T", " ")
        self.lbl_updated.configure(text=f"Updated: {updated_at}")

    def _save_current_note(self):
        if not self.selected_note_id:
            return

        title = self.ent_title.get().strip() or "Untitled Note"
        content = self.txt_content.get("1.0", "end-1c")
        pinned = 1 if self.var_pin.get() else 0
        cat = self.opt_category.get()

        sel_name = self.opt_subject.get()
        sid = None
        for s in self.subjects:
            if s["name"] == sel_name:
                sid = s["id"]
                break

        database.update_note(
            note_id=self.selected_note_id,
            title=title,
            content=content,
            subject_id=sid,
            category=cat,
            pinned=pinned
        )
        ToastNotification.show(self.winfo_toplevel(), "Note saved.", color_theme="pink")
        self.refresh()

    def _delete_current_note(self):
        if not self.selected_note_id:
            return
        database.delete_note(self.selected_note_id)
        self.selected_note_id = None
        ToastNotification.show(self.winfo_toplevel(), "Note deleted.", color_theme="blue")
        self.refresh()

    def _open_create_note_modal(self):
        def on_saved(data):
            new_id = database.add_note(
                title=data["title"],
                content=data["content"],
                subject_id=data["subject_id"],
                category=data["category"],
                pinned=data["pinned"]
            )
            self.selected_note_id = new_id
            ToastNotification.show(self.winfo_toplevel(), "Note created.", color_theme="pink")
            self.refresh()

        NoteModal(self.winfo_toplevel(), on_saved)

    def _handle_quick_capture(self):
        text = self.ent_quick.get().strip()
        if not text:
            return
        new_id = database.add_note(
            title=f"Quick Capture ({date.today().strftime('%b %d')})",
            content=text,
            category="Quick Capture"
        )
        self.ent_quick.delete(0, "end")
        self.selected_note_id = new_id
        ToastNotification.show(self.winfo_toplevel(), "Quick note captured.", color_theme="mint")
        self.refresh()

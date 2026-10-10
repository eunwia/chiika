"""
ui/corkboard_view.py - Interactive Corkboard with Draggable Sticky Notes
Provides a virtual corkboard where users can freely drag, drop, and pin notes.
Coordinates and dates are persisted to SQLite in real time.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Optional, Dict, Any
from theme import Theme
import database
import icons
from ui.components.modal import StickyNoteModal
from ui.components.toast import ToastNotification


class CorkboardView(ctk.CTkFrame):
    """Interactive Draggable Corkboard canvas with modern sticky notes."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self.note_windows: Dict[int, Any] = {}
        self.drag_data: Dict[str, Any] = {"x": 0, "y": 0, "note_id": None, "win_id": None}

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        # Header & Action Toolbar
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(16, 12))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Interactive Corkboard",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Pin colorful sticky notes, reminders, and study tips. Drag them freely around.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        btn_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_box.pack(side="right")

        btn_realign = ctk.CTkButton(
            btn_box,
            text="Tidy Up",
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=10,
            height=36,
            command=self._tidy_up_notes
        )
        btn_realign.pack(side="left", padx=(0, 10))

        ic_plus = icons.get_icon("plus", size=14, color="#FFFFFF")
        btn_add = ctk.CTkButton(
            btn_box,
            text=" Add Sticky Note",
            image=ic_plus,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=36,
            command=self._open_add_note_modal
        )
        btn_add.pack(side="left")

        # Corkboard Canvas Outer Frame
        cork_outer = ctk.CTkFrame(
            self,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        cork_outer.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        cork_bg_color = colors.get("cork_bg", "#EFE6DA")
        self.canvas = tk.Canvas(
            cork_outer,
            bg=cork_bg_color,
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.pack(fill="both", expand=True, padx=3, pady=3)

        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        w, h = event.width, event.height
        last_w, last_h = getattr(self, "_last_cork_size", (0, 0))
        if abs(w - last_w) < 80 and abs(h - last_h) < 80:
            return

        self._last_cork_size = (w, h)
        colors = Theme.current()
        self.canvas.delete("cork_decor")
        dot_color = colors.get("cork_dot", "#E2D8C9")
        
        # Subtle texture dots
        for x in range(30, w, 80):
            for y in range(30, h, 80):
                self.canvas.create_oval(x, y, x + 3, y + 3, fill=dot_color, outline="", tags="cork_decor")
        
        self.canvas.tag_lower("cork_decor")

    def refresh(self):
        for win_id in self.note_windows.values():
            try:
                self.canvas.delete(win_id)
            except Exception:
                pass
        self.note_windows.clear()

        notes = database.get_all_sticky_notes()
        for note in notes:
            self._render_note_item(note)

    def _render_note_item(self, note: dict):
        colors = Theme.current()
        note_id = note["id"]
        x = note.get("x", 60)
        y = note.get("y", 60)
        note_color = note.get("color", "#FEF3C7")
        title = note.get("title", "Note")
        content = note.get("content", "")
        date_tag = note.get("date_tag")

        note_frame = ctk.CTkFrame(
            self.canvas,
            fg_color=note_color,
            corner_radius=12,
            border_width=1,
            border_color="#D8CEBD",
            width=230,
            height=180
        )
        note_frame.pack_propagate(False)

        top_bar = ctk.CTkFrame(note_frame, fg_color="transparent", height=28)
        top_bar.pack(fill="x", padx=10, pady=(8, 2))
        top_bar.pack_propagate(False)

        pin_ic = icons.get_icon("pin", size=14, color=colors["accent_pink"])
        lbl_pin = ctk.CTkLabel(top_bar, image=pin_ic, text="")
        lbl_pin.pack(side="left", padx=(0, 4))

        lbl_title = ctk.CTkLabel(
            top_bar,
            text=title,
            font=Theme.font_subheader(),
            text_color="#2D2630",
            anchor="w"
        )
        lbl_title.pack(side="left", fill="x", expand=True)

        ic_del = icons.get_icon("x", size=11, color="#A64452")
        btn_del = ctk.CTkButton(
            top_bar,
            text="",
            image=ic_del,
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#F8D7DA",
            command=lambda nid=note_id: self._delete_note(nid)
        )
        btn_del.pack(side="right")

        ic_edit = icons.get_icon("edit", size=11, color="#64594A")
        btn_edit = ctk.CTkButton(
            top_bar,
            text="",
            image=ic_edit,
            width=20,
            height=20,
            fg_color="transparent",
            hover_color="#ECE3D4",
            command=lambda n=note: self._open_edit_note_modal(n)
        )
        btn_edit.pack(side="right", padx=(0, 2))

        txt_body = ctk.CTkLabel(
            note_frame,
            text=content,
            font=Theme.font_body(),
            text_color="#3A322D",
            wraplength=205,
            justify="left",
            anchor="nw"
        )
        txt_body.pack(fill="both", expand=True, padx=12, pady=(4, 4))

        if date_tag:
            ftr = ctk.CTkFrame(note_frame, fg_color="transparent")
            ftr.pack(fill="x", padx=12, pady=(0, 8), side="bottom")

            lbl_date = ctk.CTkLabel(
                ftr,
                text=date_tag,
                font=Theme.font_tag(),
                text_color="#736658"
            )
            lbl_date.pack(side="left")

        win_id = self.canvas.create_window(x, y, window=note_frame, anchor="nw")
        self.note_windows[note_id] = win_id

        # Bind dragging
        draggable_widgets = [note_frame, top_bar, lbl_pin, lbl_title, txt_body]
        for w in draggable_widgets:
            w.bind("<Button-1>", lambda e, nid=note_id, wid=win_id, nf=note_frame: self._start_drag(e, nid, wid, nf))
            w.bind("<B1-Motion>", lambda e, nid=note_id, wid=win_id: self._on_drag(e, nid, wid))
            w.bind("<ButtonRelease-1>", lambda e, nid=note_id, wid=win_id: self._end_drag(e, nid, wid))

    def _start_drag(self, event, note_id: int, win_id: int, note_frame: Any):
        self.canvas.tag_raise(win_id)
        coords = self.canvas.coords(win_id)
        cur_x = coords[0] if coords else 50
        cur_y = coords[1] if coords else 50

        self.drag_data = {
            "start_mouse_x": event.x_root,
            "start_mouse_y": event.y_root,
            "start_note_x": cur_x,
            "start_note_y": cur_y,
            "note_id": note_id,
            "win_id": win_id
        }

    def _on_drag(self, event, note_id: int, win_id: int):
        if self.drag_data.get("win_id") != win_id:
            return

        dx = event.x_root - self.drag_data["start_mouse_x"]
        dy = event.y_root - self.drag_data["start_mouse_y"]

        new_x = max(10, self.drag_data["start_note_x"] + dx)
        new_y = max(10, self.drag_data["start_note_y"] + dy)

        self.canvas.coords(win_id, new_x, new_y)

    def _end_drag(self, event, note_id: int, win_id: int):
        if self.drag_data.get("win_id") != win_id:
            return

        coords = self.canvas.coords(win_id)
        if coords:
            final_x = int(coords[0])
            final_y = int(coords[1])
            database.update_sticky_note_position(note_id, final_x, final_y)

        self.drag_data = {}

    def _tidy_up_notes(self):
        notes = database.get_all_sticky_notes()
        start_x = 40
        start_y = 40
        card_w = 250
        card_h = 200
        cols = 3

        for i, n in enumerate(notes):
            row = i // cols
            col = i % cols
            nx = start_x + col * card_w
            ny = start_y + row * card_h
            database.update_sticky_note_position(n["id"], nx, ny)

        ToastNotification.show(self.winfo_toplevel(), "Corkboard aligned.", color_theme="yellow")
        self.refresh()

    def _delete_note(self, note_id: int):
        database.delete_sticky_note(note_id)
        ToastNotification.show(self.winfo_toplevel(), "Note removed from corkboard.", color_theme="blue")
        self.refresh()

    def _open_add_note_modal(self):
        def on_saved(data):
            notes = database.get_all_sticky_notes()
            offset = (len(notes) * 35) % 180
            database.add_sticky_note(
                title=data["title"],
                content=data["content"],
                color=data["color"],
                x=50 + offset,
                y=50 + offset,
                date_tag=data.get("date_tag")
            )
            ToastNotification.show(self.winfo_toplevel(), "Sticky note pinned.", color_theme="pink")
            self.refresh()

        StickyNoteModal(self.winfo_toplevel(), on_saved)

    def _open_edit_note_modal(self, note: dict):
        def on_saved(data):
            database.update_sticky_note_content(
                note_id=data["id"],
                title=data["title"],
                content=data["content"],
                color=data["color"],
                date_tag=data.get("date_tag")
            )
            ToastNotification.show(self.winfo_toplevel(), "Sticky note updated.", color_theme="pink")
            self.refresh()

        StickyNoteModal(self.winfo_toplevel(), on_saved, note_data=note)

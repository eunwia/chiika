"""
ui/corkboard_view.py - Interactive Corkboard with Draggable Sticky Notes
Provides a virtual corkboard where users can freely drag, drop, and pin notes.
Coordinates and dates are persisted to SQLite in real time.
Refactored with PageHeader, PrimaryButton, SecondaryButton, and modern typography.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Optional, Dict, Any
from theme import Theme
import database
import icons
from ui.components.widgets import PageHeader, PrimaryButton, SecondaryButton
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

        # 1. Page Header with Actions
        header = PageHeader(
            self,
            title="Interactive Corkboard",
            subtitle="Pin colorful sticky notes, reminders, and study tips. Drag them freely around."
        )
        header.pack(fill="x", padx=24, pady=(20, 14))

        btn_realign = SecondaryButton(
            header.actions_container,
            text="Tidy Up",
            width=100,
            height=Theme.BTN_HEIGHT,
            command=self._tidy_up_notes
        )
        btn_realign.pack(side="left", padx=(0, 10))

        ic_plus = icons.get_icon("plus", size=16, color="#FFFFFF")
        btn_add = PrimaryButton(
            header.actions_container,
            text=" Add Sticky Note",
            image=ic_plus,
            command=self._open_add_note_modal,
            width=165,
            height=Theme.BTN_HEIGHT
        )
        btn_add.pack(side="left")

        # 2. Corkboard Canvas Outer Frame
        cork_outer = ctk.CTkFrame(
            self,
            fg_color=colors["bg_card"],
            corner_radius=Theme.RADIUS_XL,
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
            corner_radius=14,
            border_width=1,
            border_color="#D8CEBD",
            width=240,
            height=190
        )
        note_frame.pack_propagate(False)

        top_bar = ctk.CTkFrame(note_frame, fg_color="transparent", height=32)
        top_bar.pack(fill="x", padx=12, pady=(10, 2))
        top_bar.pack_propagate(False)

        pin_ic = icons.get_icon("pin", size=16, color=colors["accent_pink"])
        lbl_pin = ctk.CTkLabel(top_bar, image=pin_ic, text="")
        lbl_pin.pack(side="left", padx=(0, 6))

        lbl_title = ctk.CTkLabel(
            top_bar,
            text=title,
            font=Theme.font_subheader(),
            text_color="#2D2630",
            anchor="w"
        )
        lbl_title.pack(side="left", fill="x", expand=True)

        ic_del = icons.get_icon("x", size=13, color="#A64452")
        btn_del = ctk.CTkButton(
            top_bar,
            text="",
            image=ic_del,
            width=24,
            height=24,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#F8D7DA",
            command=lambda nid=note_id: self._delete_note(nid)
        )
        btn_del.pack(side="right")

        ic_edit = icons.get_icon("edit", size=13, color="#64594A")
        btn_edit = ctk.CTkButton(
            top_bar,
            text="",
            image=ic_edit,
            width=24,
            height=24,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#ECE3D4",
            command=lambda n=note: self._open_edit_note_modal(n)
        )
        btn_edit.pack(side="right", padx=(0, 4))

        txt_body = ctk.CTkLabel(
            note_frame,
            text=content,
            font=Theme.font_body(),
            text_color="#3A322D",
            wraplength=215,
            justify="left",
            anchor="nw"
        )
        txt_body.pack(fill="both", expand=True, padx=14, pady=(4, 4))

        if date_tag:
            ftr = ctk.CTkFrame(note_frame, fg_color="transparent")
            ftr.pack(fill="x", padx=14, pady=(0, 10), side="bottom")

            lbl_date = ctk.CTkLabel(
                ftr,
                text=date_tag,
                font=Theme.font_tag(),
                text_color="#807261",
                anchor="w"
            )
            lbl_date.pack(side="left")

        # Create Canvas Window
        win_id = self.canvas.create_window(x, y, window=note_frame, anchor="nw")
        self.note_windows[note_id] = win_id

        # Bind Drag events to header and card frame
        for widget in [note_frame, top_bar, lbl_pin, lbl_title]:
            widget.bind("<Button-1>", lambda e, nid=note_id, wid=win_id: self._start_drag(e, nid, wid))
            widget.bind("<B1-Motion>", self._on_drag)
            widget.bind("<ButtonRelease-1>", self._end_drag)

    def _start_drag(self, event, note_id: int, win_id: int):
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        self.drag_data["note_id"] = note_id
        self.drag_data["win_id"] = win_id
        self.canvas.tag_raise(win_id)

    def _on_drag(self, event):
        win_id = self.drag_data.get("win_id")
        if not win_id:
            return

        dx = event.x_root - self.drag_data["x"]
        dy = event.y_root - self.drag_data["y"]
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

        curr_coords = self.canvas.coords(win_id)
        if curr_coords:
            new_x = max(10, min(self.canvas.winfo_width() - 250, curr_coords[0] + dx))
            new_y = max(10, min(self.canvas.winfo_height() - 200, curr_coords[1] + dy))
            self.canvas.coords(win_id, new_x, new_y)

    def _end_drag(self, event):
        note_id = self.drag_data.get("note_id")
        win_id = self.drag_data.get("win_id")
        if note_id and win_id:
            coords = self.canvas.coords(win_id)
            if coords:
                database.update_sticky_note_position(note_id, int(coords[0]), int(coords[1]))
        self.drag_data = {"x": 0, "y": 0, "note_id": None, "win_id": None}

    def _tidy_up_notes(self):
        notes = database.get_all_sticky_notes()
        start_x, start_y = 30, 30
        col_w, row_h = 260, 210
        max_w = max(500, self.canvas.winfo_width() - 50)
        cols = max(1, max_w // col_w)

        for i, note in enumerate(notes):
            row = i // cols
            col = i % cols
            x = start_x + col * col_w
            y = start_y + row * row_h
            database.update_sticky_note_position(note["id"], x, y)

        self.refresh()
        ToastNotification.show(self.winfo_toplevel(), "Corkboard tidied up neatly.", color_theme="yellow")

    def _delete_note(self, note_id: int):
        database.delete_sticky_note(note_id)
        self.refresh()
        ToastNotification.show(self.winfo_toplevel(), "Sticky note removed.", color_theme="pink")

    def _open_add_note_modal(self):
        def on_saved(data):
            offset_x = 40 + (len(self.note_windows) % 5) * 50
            offset_y = 40 + (len(self.note_windows) % 4) * 45
            database.add_sticky_note(
                title=data["title"],
                content=data["content"],
                color=data["color"],
                x=offset_x,
                y=offset_y,
                date_tag=data.get("date_tag")
            )
            ToastNotification.show(self.winfo_toplevel(), "Sticky note pinned.", color_theme="pink")
            self.refresh()

        StickyNoteModal(self.winfo_toplevel(), on_saved)

    def _open_edit_note_modal(self, note: dict):
        def on_saved(data):
            database.update_sticky_note(
                note_id=data["id"],
                title=data["title"],
                content=data["content"],
                color=data["color"],
                date_tag=data.get("date_tag")
            )
            ToastNotification.show(self.winfo_toplevel(), "Sticky note updated.", color_theme="pink")
            self.refresh()

        StickyNoteModal(self.winfo_toplevel(), on_saved, note_data=note)

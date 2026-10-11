"""
ui/components/modal.py - Robust Modern Modal Dialogs for Chiikawa Study Planner
Guarantees visible, anchored primary action buttons (Save / Create / Submit) and Cancel buttons.
Includes required field validation, error messages, and Enter-to-submit bindings.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date, timedelta
from typing import Optional, Callable, Dict, Any, List
from theme import Theme
import database
import icons


class BaseModal(ctk.CTkToplevel):
    """
    Base dialog with a guaranteed pinned footer for action buttons.
    The footer is packed before the scrollable content to ensure it is ALWAYS visible.
    """

    def __init__(self, parent: Any, title_text: str, width: int = 480, height: int = 540):
        super().__init__(parent)
        self.title(title_text)
        self.geometry(f"{width}x{height}")
        self.minsize(420, 400)
        self.transient(parent)
        self.grab_set()

        colors = Theme.current()
        self.configure(fg_color=colors["bg_app"])

        # Center on parent window
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + max(0, (pw - width) // 2)
            y = py + max(0, (ph - height) // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

        # 1. Pinned Header (Top)
        self.header_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=0, height=54)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        h_inner = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        h_inner.pack(fill="both", expand=True, padx=20)

        self.lbl_title = ctk.CTkLabel(
            h_inner,
            text=title_text,
            font=Theme.font_header(),
            text_color=colors["text_primary"]
        )
        self.lbl_title.pack(side="left", pady=14)

        btn_close = ctk.CTkButton(
            h_inner,
            text="",
            image=icons.get_icon("x", size=14, color=colors["text_secondary"]),
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            command=self.destroy
        )
        btn_close.pack(side="right", pady=13)

        # 2. Pinned Footer (Bottom) - PACKED BEFORE CONTENT TO PREVENT OVERFLOW CLIPPING
        self.footer_frame = ctk.CTkFrame(
            self,
            fg_color=colors["bg_card"],
            corner_radius=0,
            height=72,
            border_width=1,
            border_color=colors["border_subtle"]
        )
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)

        self.footer_inner = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.footer_inner.pack(fill="both", expand=True, padx=20, pady=14)

        # Error notification label inside footer
        self.lbl_error = ctk.CTkLabel(
            self.footer_inner,
            text="",
            font=Theme.font_small(),
            text_color="#D94161",
            anchor="w"
        )
        self.lbl_error.pack(side="left", fill="x", expand=True)

        # 3. Middle Scrollable Content (Takes remaining space)
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(12, 8))

        self.is_submitting = False

    def show_error(self, message: str):
        self.lbl_error.configure(text=message)

    def clear_error(self):
        self.lbl_error.configure(text="")


class TaskModal(BaseModal):
    """Dialog to create or edit a task with guaranteed primary action."""

    def __init__(self, parent: Any, on_save: Callable[[Dict[str, Any]], None], task_data: Optional[Dict[str, Any]] = None):
        is_edit = bool(task_data)
        title = "Edit Task" if is_edit else "New Task"
        super().__init__(parent, title, width=480, height=560)
        self.on_save = on_save
        self.task_data = task_data or {}
        colors = Theme.current()

        # Task Title
        ctk.CTkLabel(self.content_frame, text="Task Title *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_title = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="What needs to be done?",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_title.pack(fill="x", pady=(0, 12))
        self.ent_title.bind("<Return>", lambda e: self._save())
        if task_data and task_data.get("title"):
            self.ent_title.insert(0, task_data["title"])

        # Description
        ctk.CTkLabel(self.content_frame, text="Description & Notes", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.txt_desc = ctk.CTkTextbox(
            self.content_frame,
            height=65,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1
        )
        self.txt_desc.pack(fill="x", pady=(0, 12))
        if task_data and task_data.get("description"):
            self.txt_desc.insert("1.0", task_data["description"])

        # Subject selection
        ctk.CTkLabel(self.content_frame, text="Course / Subject", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.subjects = database.get_all_subjects()
        subject_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        
        selected_subject_name = "General (No Subject)"
        if task_data and task_data.get("subject_id"):
            for s in self.subjects:
                if s["id"] == task_data["subject_id"]:
                    selected_subject_name = s["name"]
                    break

        self.opt_subject = ctk.CTkOptionMenu(
            self.content_frame,
            values=subject_names,
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_text_color=colors["text_primary"],
            height=34
        )
        self.opt_subject.set(selected_subject_name)
        self.opt_subject.pack(fill="x", pady=(0, 12))

        # Two columns for Category & Priority
        grid_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid_row.pack(fill="x", pady=(0, 12))
        grid_row.grid_columnconfigure((0, 1), weight=1)

        # Category
        ctk.CTkLabel(grid_row, text="Category", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.opt_cat = ctk.CTkOptionMenu(
            grid_row,
            values=["Study", "Homework", "Exam Prep", "Reading", "Project", "Personal"],
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_cat.set(task_data.get("category", "Study") if task_data else "Study")
        self.opt_cat.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        # Priority
        ctk.CTkLabel(grid_row, text="Priority", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.opt_priority = ctk.CTkOptionMenu(
            grid_row,
            values=["High", "Medium", "Low"],
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_priority.set(task_data.get("priority", "Medium") if task_data else "Medium")
        self.opt_priority.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        # Due Date Row
        ctk.CTkLabel(self.content_frame, text="Due Date (YYYY-MM-DD)", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        date_box = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        date_box.pack(fill="x", pady=(0, 4))

        init_due = task_data.get("due_date", date.today().isoformat()) if task_data else date.today().isoformat()
        self.ent_date = ctk.CTkEntry(
            date_box,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34,
            width=160
        )
        self.ent_date.insert(0, init_due or "")
        self.ent_date.pack(side="left", padx=(0, 8))

        btn_today = ctk.CTkButton(
            date_box,
            text="Today",
            width=65,
            height=32,
            font=Theme.font_small(),
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            hover_color=colors["bg_sidebar_hover"],
            command=lambda: self.set_date(date.today().isoformat())
        )
        btn_today.pack(side="left", padx=(0, 6))

        btn_tom = ctk.CTkButton(
            date_box,
            text="Tomorrow",
            width=75,
            height=32,
            font=Theme.font_small(),
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            hover_color=colors["bg_sidebar_hover"],
            command=lambda: self.set_date((date.today() + timedelta(days=1)).isoformat())
        )
        btn_tom.pack(side="left")

        # Pinned Footer Action Buttons
        btn_cancel = ctk.CTkButton(
            self.footer_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["text_secondary"],
            border_width=1,
            border_color=colors["border"],
            height=36,
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_label = "Update Task" if is_edit else "Save Task"
        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text=btn_label,
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=36,
            width=115,
            command=self._save
        )
        self.btn_submit.pack(side="right")

        self.ent_title.focus_set()

    def set_date(self, d_str: str):
        self.ent_date.delete(0, "end")
        self.ent_date.insert(0, d_str)

    def _save(self):
        if self.is_submitting:
            return

        title = self.ent_title.get().strip()
        if not title:
            self.show_error("Please enter a task title.")
            self.ent_title.configure(border_color="#D94161")
            self.ent_title.focus_set()
            return

        self.clear_error()
        self.is_submitting = True
        self.btn_submit.configure(state="disabled")

        desc = self.txt_desc.get("1.0", "end-1c").strip()
        cat = self.opt_cat.get()
        prio = self.opt_priority.get()
        d_date = self.ent_date.get().strip() or None

        sel_name = self.opt_subject.get()
        subject_id = None
        for s in self.subjects:
            if s["name"] == sel_name:
                subject_id = s["id"]
                break

        payload = {
            "title": title,
            "description": desc,
            "subject_id": subject_id,
            "category": cat,
            "priority": prio,
            "due_date": d_date,
            "due_time": "23:59"
        }
        if "id" in self.task_data:
            payload["id"] = self.task_data["id"]

        self.on_save(payload)
        self.destroy()


class StickyNoteModal(BaseModal):
    """Dialog to create or edit a Corkboard Sticky Note."""

    def __init__(self, parent: Any, on_save: Callable[[Dict[str, Any]], None], note_data: Optional[Dict[str, Any]] = None):
        is_edit = bool(note_data)
        title = "Edit Sticky Note" if is_edit else "New Sticky Note"
        super().__init__(parent, title, width=440, height=480)
        self.on_save = on_save
        self.note_data = note_data or {}
        colors = Theme.current()

        # Title
        ctk.CTkLabel(self.content_frame, text="Note Title", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_title = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Study Tip, Formula, Reminder",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_title.pack(fill="x", pady=(0, 12))
        if note_data and note_data.get("title"):
            self.ent_title.insert(0, note_data["title"])

        # Content
        ctk.CTkLabel(self.content_frame, text="Note Content *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.txt_content = ctk.CTkTextbox(
            self.content_frame,
            height=90,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1
        )
        self.txt_content.pack(fill="x", pady=(0, 12))
        if note_data and note_data.get("content"):
            self.txt_content.insert("1.0", note_data["content"])

        # Sticky Note Color
        ctk.CTkLabel(self.content_frame, text="Color Tone", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.color_options = [
            ("#FEF3C7", "Warm Cream Yellow"),
            ("#FCE7F3", "Soft Blossom Pink"),
            ("#E0F2FE", "Serene Blue"),
            ("#DCFCE7", "Matcha Green"),
            ("#F3E8FF", "Pastel Lavender")
        ]
        self.selected_color = tk.StringVar(value=note_data.get("color", "#FEF3C7") if note_data else "#FEF3C7")

        color_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        color_row.pack(fill="x", pady=(0, 12))

        for hex_code, label in self.color_options:
            rb = ctk.CTkRadioButton(
                color_row,
                text=label,
                value=hex_code,
                variable=self.selected_color,
                font=Theme.font_small(),
                fg_color=colors["accent_pink"],
                border_color=colors["border"]
            )
            rb.pack(anchor="w", pady=2)

        # Date Tag
        ctk.CTkLabel(self.content_frame, text="Date Association (Optional)", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_date = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="YYYY-MM-DD",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        if note_data and note_data.get("date_tag"):
            self.ent_date.insert(0, note_data["date_tag"])
        self.ent_date.pack(fill="x")

        # Guaranteed Footer Actions
        btn_cancel = ctk.CTkButton(
            self.footer_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["text_secondary"],
            border_width=1,
            border_color=colors["border"],
            height=36,
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_label = "Update Note" if is_edit else "Pin Note"
        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text=btn_label,
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=36,
            width=110,
            command=self._save
        )
        self.btn_submit.pack(side="right")

        self.ent_title.focus_set()

    def _save(self):
        content = self.txt_content.get("1.0", "end-1c").strip()
        if not content:
            self.show_error("Please enter note content.")
            self.txt_content.configure(border_color="#D94161")
            self.txt_content.focus_set()
            return

        self.clear_error()
        self.btn_submit.configure(state="disabled")

        payload = {
            "title": self.ent_title.get().strip() or "Note",
            "content": content,
            "color": self.selected_color.get(),
            "date_tag": self.ent_date.get().strip() or None
        }
        if "id" in self.note_data:
            payload["id"] = self.note_data["id"]

        self.on_save(payload)
        self.destroy()


class SubjectModal(BaseModal):
    """Dialog to create or edit an academic course/subject."""

    def __init__(self, parent: Any, on_save: Callable[[Dict[str, Any]], None], subject_data: Optional[Dict[str, Any]] = None):
        is_edit = bool(subject_data)
        title = "Edit Course" if is_edit else "Add Course"
        super().__init__(parent, title, width=420, height=460)
        self.on_save = on_save
        self.subject_data = subject_data or {}
        colors = Theme.current()

        ctk.CTkLabel(self.content_frame, text="Course / Subject Name *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_name = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Mathematics, Computer Science, Literature",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_name.pack(fill="x", pady=(0, 12))
        self.ent_name.bind("<Return>", lambda e: self._save())
        if subject_data and subject_data.get("name"):
            self.ent_name.insert(0, subject_data["name"])

        # Color Accent
        ctk.CTkLabel(self.content_frame, text="Course Color Theme", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.color_options = [
            ("#5694D6", "Slate Blue"),
            ("#E66882", "Rose Coral"),
            ("#48A87D", "Matcha Green"),
            ("#E5A038", "Warm Amber"),
            ("#8B70CF", "Cozy Lavender"),
        ]
        self.selected_color = tk.StringVar(value=subject_data.get("color", "#5694D6") if subject_data else "#5694D6")
        for hex_code, label in self.color_options:
            rb = ctk.CTkRadioButton(
                self.content_frame,
                text=label,
                value=hex_code,
                variable=self.selected_color,
                font=Theme.font_small(),
                fg_color=hex_code,
                border_color=colors["border"]
            )
            rb.pack(anchor="w", pady=2)

        # Description
        ctk.CTkLabel(self.content_frame, text="Description / Course Code", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(8, 4))
        self.ent_desc = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. CS101, Algorithms & Discrete Structures",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        if subject_data and subject_data.get("description"):
            self.ent_desc.insert(0, subject_data["description"])
        self.ent_desc.pack(fill="x")

        # Pinned Footer Actions
        btn_cancel = ctk.CTkButton(
            self.footer_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["text_secondary"],
            border_width=1,
            border_color=colors["border"],
            height=36,
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_label = "Save Changes" if is_edit else "Add Subject"
        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text=btn_label,
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=36,
            width=115,
            command=self._save
        )
        self.btn_submit.pack(side="right")

        self.ent_name.focus_set()

    def _save(self):
        name = self.ent_name.get().strip()
        if not name:
            self.show_error("Please enter a subject name.")
            self.ent_name.configure(border_color="#D94161")
            self.ent_name.focus_set()
            return

        self.clear_error()
        self.btn_submit.configure(state="disabled")

        payload = {
            "name": name,
            "color": self.selected_color.get(),
            "icon": "📚",
            "description": self.ent_desc.get().strip()
        }
        if "id" in self.subject_data:
            payload["id"] = self.subject_data["id"]

        self.on_save(payload)
        self.destroy()


class EventModal(BaseModal):
    """Dialog to create or edit a Calendar Event or Exam/Deadline."""

    def __init__(self, parent: Any, on_save: Callable[[Dict[str, Any]], None], event_data: Optional[Dict[str, Any]] = None, default_date: Optional[str] = None):
        is_edit = bool(event_data)
        title = "Edit Event" if is_edit else "Schedule Event"
        super().__init__(parent, title, width=460, height=500)
        self.on_save = on_save
        self.event_data = event_data or {}
        colors = Theme.current()

        ctk.CTkLabel(self.content_frame, text="Event / Deadline Title *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_title = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Midterm Exam, Essay Due, Lab Workshop",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_title.pack(fill="x", pady=(0, 12))
        self.ent_title.bind("<Return>", lambda e: self._save())
        if event_data and event_data.get("title"):
            self.ent_title.insert(0, event_data["title"])

        # Type & Course row
        grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 12))
        grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid, text="Event Type", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.opt_type = ctk.CTkOptionMenu(
            grid,
            values=["Exam", "Assignment", "Deadline", "Event", "Study Session"],
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_type.set(event_data.get("event_type", "Exam") if event_data else "Exam")
        self.opt_type.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        self.subjects = database.get_all_subjects()
        sub_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        sel_sub = "General (No Subject)"
        if event_data and event_data.get("subject_id"):
            for s in self.subjects:
                if s["id"] == event_data["subject_id"]:
                    sel_sub = s["name"]
                    break

        ctk.CTkLabel(grid, text="Course", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.opt_sub = ctk.CTkOptionMenu(
            grid,
            values=sub_names,
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_sub.set(sel_sub)
        self.opt_sub.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        # Date & Time Row
        date_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        date_row.pack(fill="x", pady=(0, 12))
        date_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(date_row, text="Date (YYYY-MM-DD) *", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.ent_start_date = ctk.CTkEntry(
            date_row,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        init_date = (event_data.get("start_date") if event_data else None) or default_date or date.today().isoformat()
        self.ent_start_date.insert(0, init_date)
        self.ent_start_date.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        ctk.CTkLabel(date_row, text="Time (HH:MM)", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.ent_start_time = ctk.CTkEntry(
            date_row,
            placeholder_text="09:00",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        self.ent_start_time.insert(0, event_data.get("start_time", "09:00") if event_data else "09:00")
        self.ent_start_time.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        # Notes
        ctk.CTkLabel(self.content_frame, text="Location / Notes", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_notes = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Room 402, online submission link, or materials",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        if event_data and event_data.get("notes"):
            self.ent_notes.insert(0, event_data["notes"])
        self.ent_notes.pack(fill="x")

        # Pinned Footer
        btn_cancel = ctk.CTkButton(
            self.footer_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["text_secondary"],
            border_width=1,
            border_color=colors["border"],
            height=36,
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_label = "Update Event" if is_edit else "Save Event"
        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text=btn_label,
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=36,
            width=115,
            command=self._save
        )
        self.btn_submit.pack(side="right")

        self.ent_title.focus_set()

    def _save(self):
        title = self.ent_title.get().strip()
        start_date = self.ent_start_date.get().strip()
        if not title or not start_date:
            self.show_error("Please enter both title and date.")
            self.ent_title.focus_set()
            return

        self.clear_error()
        self.btn_submit.configure(state="disabled")

        sel_name = self.opt_sub.get()
        subject_id = None
        for s in self.subjects:
            if s["name"] == sel_name:
                subject_id = s["id"]
                break

        payload = {
            "title": title,
            "event_type": self.opt_type.get(),
            "subject_id": subject_id,
            "start_date": start_date,
            "start_time": self.ent_start_time.get().strip() or "09:00",
            "end_date": start_date,
            "end_time": "10:00",
            "notes": self.ent_notes.get().strip()
        }
        if "id" in self.event_data:
            payload["id"] = self.event_data["id"]

        self.on_save(payload)
        self.destroy()


class HabitModal(BaseModal):
    """Dialog to create a new habit with guaranteed Save button."""

    def __init__(self, parent: Any, on_save: Callable[[Dict[str, Any]], None]):
        super().__init__(parent, "New Habit", width=420, height=380)
        self.on_save = on_save
        colors = Theme.current()

        ctk.CTkLabel(self.content_frame, text="Habit Name *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_title = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Read 20 pages, Review Flashcards, Hydrate",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_title.pack(fill="x", pady=(0, 12))
        self.ent_title.bind("<Return>", lambda e: self._save())

        # Category
        ctk.CTkLabel(self.content_frame, text="Category", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.opt_cat = ctk.CTkOptionMenu(
            self.content_frame,
            values=["Study", "Health", "Review", "Mindfulness", "Routine"],
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_cat.set("Study")
        self.opt_cat.pack(fill="x")

        # Pinned Footer
        btn_cancel = ctk.CTkButton(
            self.footer_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["text_secondary"],
            border_width=1,
            border_color=colors["border"],
            height=36,
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text="Add Habit",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=36,
            width=110,
            command=self._save
        )
        self.btn_submit.pack(side="right")

        self.ent_title.focus_set()

    def _save(self):
        title = self.ent_title.get().strip()
        if not title:
            self.show_error("Please enter a habit title.")
            self.ent_title.focus_set()
            return

        self.clear_error()
        self.btn_submit.configure(state="disabled")

        payload = {
            "title": title,
            "category": self.opt_cat.get(),
            "target_frequency": "Daily",
            "icon": "⭐"
        }
        self.on_save(payload)
        self.destroy()


class NoteModal(BaseModal):
    """Dedicated modal to create or edit a study note with clear Save button."""

    def __init__(self, parent: Any, on_save: Callable[[Dict[str, Any]], None], note_data: Optional[Dict[str, Any]] = None):
        is_edit = bool(note_data)
        title = "Edit Note" if is_edit else "Create Note"
        super().__init__(parent, title, width=520, height=540)
        self.on_save = on_save
        self.note_data = note_data or {}
        colors = Theme.current()

        ctk.CTkLabel(self.content_frame, text="Note Title *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_title = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Note Title...",
            font=Theme.font_body_bold(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_title.pack(fill="x", pady=(0, 10))
        if note_data and note_data.get("title"):
            self.ent_title.insert(0, note_data["title"])

        # Row for Course & Category
        row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))
        row.grid_columnconfigure((0, 1), weight=1)

        self.subjects = database.get_all_subjects()
        sub_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        sel_sub = "General (No Subject)"
        if note_data and note_data.get("subject_id"):
            for s in self.subjects:
                if s["id"] == note_data["subject_id"]:
                    sel_sub = s["name"]
                    break

        ctk.CTkLabel(row, text="Course", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.opt_sub = ctk.CTkOptionMenu(
            row,
            values=sub_names,
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_sub.set(sel_sub)
        self.opt_sub.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        ctk.CTkLabel(row, text="Category", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.opt_cat = ctk.CTkOptionMenu(
            row,
            values=["General", "Lecture", "Summary", "Inspiration", "Draft", "Quick Capture"],
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_cat.set(note_data.get("category", "General") if note_data else "General")
        self.opt_cat.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        # Content
        ctk.CTkLabel(self.content_frame, text="Content / Body", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.txt_content = ctk.CTkTextbox(
            self.content_frame,
            height=140,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            border_width=1
        )
        self.txt_content.pack(fill="both", expand=True)
        if note_data and note_data.get("content"):
            self.txt_content.insert("1.0", note_data["content"])

        # Pinned Footer
        btn_cancel = ctk.CTkButton(
            self.footer_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["text_secondary"],
            border_width=1,
            border_color=colors["border"],
            height=36,
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_label = "Save Note" if is_edit else "Create Note"
        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text=btn_label,
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=36,
            width=115,
            command=self._save
        )
        self.btn_submit.pack(side="right")

        self.ent_title.focus_set()

    def _save(self):
        title = self.ent_title.get().strip()
        if not title:
            self.show_error("Please enter a note title.")
            self.ent_title.focus_set()
            return

        self.clear_error()
        self.btn_submit.configure(state="disabled")

        sel_name = self.opt_sub.get()
        subject_id = None
        for s in self.subjects:
            if s["name"] == sel_name:
                subject_id = s["id"]
                break

        payload = {
            "title": title,
            "content": self.txt_content.get("1.0", "end-1c").strip(),
            "subject_id": subject_id,
            "category": self.opt_cat.get(),
            "pinned": self.note_data.get("pinned", 0) if self.note_data else 0
        }
        if "id" in self.note_data:
            payload["id"] = self.note_data["id"]

        self.on_save(payload)
        self.destroy()


class SessionModal(BaseModal):
    """Dialog to log a manual study session with guaranteed Save button."""

    def __init__(self, parent: Any, on_save: Callable[[Dict[str, Any]], None]):
        super().__init__(parent, "Log Study Session", width=420, height=440)
        self.on_save = on_save
        colors = Theme.current()

        ctk.CTkLabel(self.content_frame, text="Topic / Study Focus *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_topic = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Chapter 4 Practice, Calculus Review",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_topic.pack(fill="x", pady=(0, 12))
        self.ent_topic.bind("<Return>", lambda e: self._save())

        # Duration
        ctk.CTkLabel(self.content_frame, text="Duration (Minutes) *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_duration = ctk.CTkEntry(
            self.content_frame,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        self.ent_duration.insert(0, "45")
        self.ent_duration.pack(fill="x", pady=(0, 12))

        # Subject
        ctk.CTkLabel(self.content_frame, text="Course / Subject", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.subjects = database.get_all_subjects()
        sub_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        self.opt_sub = ctk.CTkOptionMenu(
            self.content_frame,
            values=sub_names,
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_sub.set("General (No Subject)")
        self.opt_sub.pack(fill="x", pady=(0, 12))

        # Notes
        ctk.CTkLabel(self.content_frame, text="Session Notes", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_notes = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Optional remarks or key takeaways",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        self.ent_notes.pack(fill="x")

        # Pinned Footer
        btn_cancel = ctk.CTkButton(
            self.footer_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=colors["bg_card_secondary"],
            text_color=colors["text_secondary"],
            border_width=1,
            border_color=colors["border"],
            height=36,
            width=90,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text="Save Session",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            height=36,
            width=120,
            command=self._save
        )
        self.btn_submit.pack(side="right")

        self.ent_topic.focus_set()

    def _save(self):
        topic = self.ent_topic.get().strip()
        dur_str = self.ent_duration.get().strip()

        if not topic:
            self.show_error("Please enter a study topic.")
            self.ent_topic.focus_set()
            return

        try:
            dur = int(dur_str)
            if dur <= 0:
                raise ValueError
        except ValueError:
            self.show_error("Duration must be a positive integer.")
            self.ent_duration.focus_set()
            return

        self.clear_error()
        self.btn_submit.configure(state="disabled")

        sel_name = self.opt_sub.get()
        subject_id = None
        for s in self.subjects:
            if s["name"] == sel_name:
                subject_id = s["id"]
                break

        payload = {
            "topic": topic,
            "duration_minutes": dur,
            "subject_id": subject_id,
            "notes": self.ent_notes.get().strip()
        }
        self.on_save(payload)
        self.destroy()

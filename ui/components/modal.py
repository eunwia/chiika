"""
ui/components/modal.py - Robust Modern Modal Dialogs for Chiikawa Study Planner
Guarantees visible, anchored primary action buttons (Save / Create / Submit) and Cancel buttons.
Includes required field validation, error messages, and Enter-to-submit bindings.
"""

import tkinter as tk
from tkinter import colorchooser
import customtkinter as ctk
from datetime import datetime, date, timedelta
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


class ConfirmModal(ctk.CTkToplevel):
    """
    Themed confirmation dialog with explicit Confirm and Cancel actions.
    """
    def __init__(
        self,
        parent: Any,
        title_text: str = "Confirm Delete",
        message: str = "Are you sure you want to delete this record? This action cannot be undone.",
        on_confirm: Optional[Callable[[], None]] = None,
        confirm_text: str = "Delete",
        is_danger: bool = True,
        width: int = 420,
        height: int = 220
    ):
        super().__init__(parent)
        self.title(title_text)
        self.geometry(f"{width}x{height}")
        self.minsize(360, 200)
        self.transient(parent)
        self.grab_set()

        colors = Theme.current()
        self.configure(fg_color=(Theme.LIGHT["bg_app"], Theme.DARK["bg_app"]))
        self.on_confirm = on_confirm

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

        # Pinned Header
        header = ctk.CTkFrame(self, fg_color=(Theme.LIGHT["bg_card"], Theme.DARK["bg_card"]), corner_radius=0, height=50)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(fill="both", expand=True, padx=20)

        ctk.CTkLabel(
            h_inner,
            text=title_text,
            font=Theme.font_header(),
            text_color=(Theme.LIGHT["text_primary"], Theme.DARK["text_primary"])
        ).pack(side="left", pady=12)

        btn_close = ctk.CTkButton(
            h_inner,
            text="",
            image=icons.get_icon("x", size=14, color=colors["text_secondary"]),
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=(Theme.LIGHT["bg_card_secondary"], Theme.DARK["bg_card_secondary"]),
            command=self.destroy
        )
        btn_close.pack(side="right", pady=11)

        # Footer
        footer = ctk.CTkFrame(
            self,
            fg_color=(Theme.LIGHT["bg_card"], Theme.DARK["bg_card"]),
            corner_radius=0,
            height=60,
            border_width=1,
            border_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"])
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        f_inner = ctk.CTkFrame(footer, fg_color="transparent")
        f_inner.pack(fill="both", expand=True, padx=20, pady=12)

        btn_cancel = ctk.CTkButton(
            f_inner,
            text="Cancel",
            font=Theme.font_body(),
            fg_color="transparent",
            hover_color=(Theme.LIGHT["bg_card_secondary"], Theme.DARK["bg_card_secondary"]),
            text_color=(Theme.LIGHT["text_secondary"], Theme.DARK["text_secondary"]),
            border_width=1,
            border_color=(Theme.LIGHT["border"], Theme.DARK["border"]),
            height=36,
            width=85,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_action = ctk.CTkButton(
            f_inner,
            text=confirm_text,
            font=Theme.font_body_bold(),
            fg_color=(Theme.LIGHT["priority_high_bg"], Theme.DARK["priority_high_bg"]) if is_danger else (Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"]),
            hover_color=(Theme.LIGHT["accent_pink_hover"], Theme.DARK["accent_pink_hover"]),
            border_width=1 if is_danger else 0,
            border_color=(Theme.LIGHT["priority_high_fg"], Theme.DARK["priority_high_fg"]) if is_danger else "transparent",
            text_color=(Theme.LIGHT["priority_high_fg"], Theme.DARK["priority_high_fg"]) if is_danger else "#FFFFFF",
            height=36,
            width=95,
            command=self._handle_confirm
        )
        btn_action.pack(side="right")

        # Body Message
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            body,
            text=message,
            font=Theme.font_body(),
            text_color=(Theme.LIGHT["text_primary"], Theme.DARK["text_primary"]),
            wraplength=width - 40,
            justify="left"
        ).pack(anchor="w")

    def _handle_confirm(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()


class TaskModal(BaseModal):
    """Dialog to create or edit a task with guaranteed primary action."""

    def __init__(
        self,
        parent: Any,
        on_save: Callable[[Dict[str, Any]], None],
        task_data: Optional[Dict[str, Any]] = None,
        default_task_type: str = "daily"
    ):
        is_edit = bool(task_data)
        title = "Edit Task" if is_edit else "New Task"
        super().__init__(parent, title, width=480, height=600)
        self.on_save = on_save
        self.task_data = task_data or {}
        colors = Theme.current()

        # Task Type (Daily / General)
        ctk.CTkLabel(self.content_frame, text="Task Section", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.seg_type = ctk.CTkSegmentedButton(
            self.content_frame,
            values=["Daily Tasks", "General Tasks"],
            font=Theme.font_body(),
            height=34,
            corner_radius=10,
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card"],
            unselected_hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"]
        )
        init_is_general = (task_data and task_data.get("task_type") == "general") or (not task_data and default_task_type == "general")
        self.seg_type.set("General Tasks" if init_is_general else "Daily Tasks")
        self.seg_type.pack(fill="x", pady=(0, 12))

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

        t_type = "general" if self.seg_type.get() == "General Tasks" else "daily"
        payload = {
            "title": title,
            "description": desc,
            "subject_id": subject_id,
            "category": cat,
            "priority": prio,
            "due_date": d_date,
            "due_time": "23:59",
            "task_type": t_type
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


PASTEL_SWATCHES = [
    "#FF7597",  # Rose Pink
    "#5B9BD5",  # Sky Blue
    "#42B883",  # Matcha Mint
    "#F5A623",  # Golden Amber
    "#9A7BD6",  # Cozy Lavender
    "#F08CBA",  # Sweet Berry
    "#FF9AA2",  # Salmon
    "#B5EAD7",  # Mint Cream
    "#C7CEEA",  # Periwinkle
    "#FFEAA7",  # Butter Yellow
]


class EventModal(BaseModal):
    """Dialog to create, edit, or duplicate a Calendar Event or Exam/Deadline with custom color coding."""

    def __init__(
        self,
        parent: Any,
        on_save: Callable[[Dict[str, Any]], None],
        event_data: Optional[Dict[str, Any]] = None,
        default_date: Optional[str] = None,
        on_duplicate: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None
    ):
        is_edit = bool(event_data)
        title = "Edit Event" if is_edit else "Schedule Event"
        super().__init__(parent, title, width=500, height=690)
        self.on_save = on_save
        self.on_duplicate = on_duplicate
        self.on_delete = on_delete
        self.event_data = event_data or {}
        colors = Theme.current()

        # 1. Title
        ctk.CTkLabel(self.content_frame, text="Event / Deadline Title *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_title = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Midterm Exam, Essay Due, Lab Workshop",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_title.pack(fill="x", pady=(0, 10))
        self.ent_title.bind("<Return>", lambda e: self._save())
        if event_data and event_data.get("title"):
            self.ent_title.insert(0, event_data["title"])

        # 2. Category & Course Row
        cat_course_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cat_course_row.pack(fill="x", pady=(0, 10))
        cat_course_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(cat_course_row, text="Category *", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.categories = database.get_event_categories()
        cat_names = [c["name"] for c in self.categories]
        if not cat_names:
            cat_names = ["Exams", "Assignments", "Study Sessions", "Deadlines", "Personal", "Other"]

        init_cat = self.event_data.get("category") or self.event_data.get("event_type") or "Exams"
        if init_cat not in cat_names:
            found = next((cn for cn in cat_names if cn.lower() == init_cat.lower()), None)
            if found:
                init_cat = found
            else:
                cat_names.append(init_cat)

        self.opt_category = ctk.CTkOptionMenu(
            cat_course_row,
            values=cat_names,
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34,
            command=self._on_category_selected
        )
        self.opt_category.set(init_cat)
        self.opt_category.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        # Course dropdown
        self.subjects = database.get_all_subjects()
        sub_names = ["General (No Subject)"] + [s["name"] for s in self.subjects]
        sel_sub = "General (No Subject)"
        if self.event_data.get("subject_id"):
            for s in self.subjects:
                if s["id"] == self.event_data["subject_id"]:
                    sel_sub = s["name"]
                    break

        ctk.CTkLabel(cat_course_row, text="Course (Optional)", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.opt_sub = ctk.CTkOptionMenu(
            cat_course_row,
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

        # 3. Color Selection Section
        self.selected_color = self.event_data.get("color") or database.get_category_color(init_cat)
        self._user_picked_custom_color = bool(self.event_data.get("color"))

        color_section = ctk.CTkFrame(self.content_frame, fg_color=colors["bg_card_secondary"], corner_radius=10)
        color_section.pack(fill="x", pady=(0, 10))
        c_inner = ctk.CTkFrame(color_section, fg_color="transparent")
        c_inner.pack(fill="x", padx=10, pady=8)

        color_top = ctk.CTkFrame(c_inner, fg_color="transparent")
        color_top.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(color_top, text="Event Color:", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(side="left")

        self.lbl_color_badge = ctk.CTkLabel(
            color_top,
            text="  Preview  ",
            font=Theme.font_tag(),
            fg_color=self.selected_color,
            text_color=database.get_contrast_text_color(self.selected_color),
            corner_radius=6
        )
        self.lbl_color_badge.pack(side="left", padx=(10, 0))

        # Swatch bar
        swatch_frame = ctk.CTkFrame(c_inner, fg_color="transparent")
        swatch_frame.pack(fill="x")

        self.swatch_buttons = []
        for hex_col in PASTEL_SWATCHES:
            btn_s = ctk.CTkButton(
                swatch_frame,
                text="",
                width=24,
                height=24,
                corner_radius=12,
                fg_color=hex_col,
                hover_color=hex_col,
                border_width=2 if hex_col.lower() == self.selected_color.lower() else 0,
                border_color=colors["text_primary"],
                command=lambda c=hex_col: self._select_color(c)
            )
            btn_s.pack(side="left", padx=2)
            self.swatch_buttons.append((hex_col, btn_s))

        btn_pick_custom = ctk.CTkButton(
            swatch_frame,
            text="Custom...",
            font=Theme.font_tag(),
            width=65,
            height=24,
            corner_radius=6,
            fg_color=colors["bg_card"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            border_width=1,
            border_color=colors["border"],
            command=self._pick_custom_color
        )
        btn_pick_custom.pack(side="left", padx=(6, 0))

        # 4. Date & Quick Buttons
        date_section = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        date_section.pack(fill="x", pady=(0, 10))

        d_head = ctk.CTkFrame(date_section, fg_color="transparent")
        d_head.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(d_head, text="Date (YYYY-MM-DD) *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(side="left")

        btn_tmrw = ctk.CTkButton(
            d_head,
            text="Tomorrow",
            font=Theme.font_tag(),
            width=62,
            height=22,
            fg_color="transparent",
            text_color=colors["accent_pink"],
            hover_color=colors["bg_card_secondary"],
            command=lambda: self._set_date((date.today() + timedelta(days=1)).isoformat())
        )
        btn_tmrw.pack(side="right")

        btn_today = ctk.CTkButton(
            d_head,
            text="Today",
            font=Theme.font_tag(),
            width=48,
            height=22,
            fg_color="transparent",
            text_color=colors["accent_pink"],
            hover_color=colors["bg_card_secondary"],
            command=lambda: self._set_date(date.today().isoformat())
        )
        btn_today.pack(side="right", padx=(0, 4))

        self.ent_start_date = ctk.CTkEntry(
            date_section,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        init_date = (event_data.get("start_date") if event_data else None) or default_date or date.today().isoformat()
        self.ent_start_date.insert(0, init_date)
        self.ent_start_date.pack(fill="x")

        # 5. Start Time & End Time Row
        time_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        time_row.pack(fill="x", pady=(0, 10))
        time_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(time_row, text="Start Time (HH:MM) *", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.ent_start_time = ctk.CTkEntry(
            time_row,
            placeholder_text="09:00",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        self.ent_start_time.insert(0, event_data.get("start_time", "09:00") if event_data else "09:00")
        self.ent_start_time.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        ctk.CTkLabel(time_row, text="End Time (HH:MM) *", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.ent_end_time = ctk.CTkEntry(
            time_row,
            placeholder_text="10:00",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        self.ent_end_time.insert(0, event_data.get("end_time", "10:00") if event_data else "10:00")
        self.ent_end_time.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        # 6. Location Field
        ctk.CTkLabel(self.content_frame, text="Location (Optional)", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_location = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Room 402, Hall B, Online / Zoom link",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        if event_data and event_data.get("location"):
            self.ent_location.insert(0, event_data["location"])
        self.ent_location.pack(fill="x", pady=(0, 10))

        # 7. Notes Field
        ctk.CTkLabel(self.content_frame, text="Description / Notes (Optional)", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_notes = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="e.g. Bring scientific calculator, chapters 1-4",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        if event_data and event_data.get("notes"):
            self.ent_notes.insert(0, event_data["notes"])
        self.ent_notes.pack(fill="x", pady=(0, 10))

        # 8. Reminder & Recurring Options
        options_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        options_row.pack(fill="x", pady=(0, 8))
        options_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(options_row, text="Reminder (Optional)", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=0, sticky="w", padx=(0, 6))
        rem_options = ["None", "10 mins before", "15 mins before", "30 mins before", "1 hour before", "1 day before"]
        init_rem = self.event_data.get("reminder") or "None"
        if init_rem not in rem_options:
            rem_options.append(init_rem)
        self.opt_reminder = ctk.CTkOptionMenu(
            options_row,
            values=rem_options,
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_reminder.set(init_rem)
        self.opt_reminder.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(4, 0))

        ctk.CTkLabel(options_row, text="Recurring (Optional)", font=Theme.font_subheader(), text_color=colors["text_primary"]).grid(row=0, column=1, sticky="w", padx=(6, 0))
        rec_options = ["None", "Daily", "Weekly", "Bi-weekly", "Monthly"]
        init_rec = self.event_data.get("recurring") or "None"
        if init_rec not in rec_options:
            rec_options.append(init_rec)
        self.opt_recurring = ctk.CTkOptionMenu(
            options_row,
            values=rec_options,
            font=Theme.font_body(),
            fg_color=colors["bg_card"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            height=34
        )
        self.opt_recurring.set(init_rec)
        self.opt_recurring.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(4, 0))

        # Pinned Footer Action Buttons
        if is_edit:
            btn_del = ctk.CTkButton(
                self.footer_inner,
                text="Delete",
                font=Theme.font_body(),
                fg_color="transparent",
                hover_color=colors["priority_high_bg"],
                text_color=colors["priority_high_fg"],
                border_width=1,
                border_color=colors["priority_high_fg"],
                height=36,
                width=75,
                command=self._delete_current
            )
            btn_del.pack(side="left")

            btn_dup = ctk.CTkButton(
                self.footer_inner,
                text="Duplicate",
                font=Theme.font_body(),
                fg_color="transparent",
                hover_color=colors["bg_card_secondary"],
                text_color=colors["text_primary"],
                border_width=1,
                border_color=colors["border"],
                height=36,
                width=85,
                command=self._duplicate_current
            )
            btn_dup.pack(side="left", padx=(8, 0))

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
            width=80,
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

    def _set_date(self, d_str: str):
        self.ent_start_date.delete(0, "end")
        self.ent_start_date.insert(0, d_str)

    def _select_color(self, hex_col: str):
        self.selected_color = hex_col
        self._user_picked_custom_color = True
        colors = Theme.current()
        self.lbl_color_badge.configure(
            fg_color=hex_col,
            text_color=database.get_contrast_text_color(hex_col)
        )
        for c, btn in self.swatch_buttons:
            btn.configure(border_width=2 if c.lower() == hex_col.lower() else 0)

    def _pick_custom_color(self):
        res = colorchooser.askcolor(color=self.selected_color, title="Select Event Color", parent=self)
        if res and res[1]:
            self._select_color(res[1])

    def _on_category_selected(self, cat_name: str):
        if not self._user_picked_custom_color:
            cat_col = database.get_category_color(cat_name)
            self._select_color(cat_col)
            self._user_picked_custom_color = False

    def _duplicate_current(self):
        if "id" in self.event_data:
            dup_id = database.duplicate_calendar_event(self.event_data["id"])
            if self.on_duplicate and dup_id:
                self.on_duplicate(dup_id)
            self.destroy()

    def _delete_current(self):
        if "id" in self.event_data and self.on_delete:
            self.on_delete(self.event_data["id"])
            self.destroy()

    def _save(self):
        title = self.ent_title.get().strip()
        start_date = self.ent_start_date.get().strip()
        start_time = self.ent_start_time.get().strip() or "09:00"
        end_time = self.ent_end_time.get().strip() or "10:00"

        if not title:
            self.show_error("Please enter an event title.")
            self.ent_title.focus_set()
            return

        if not start_date:
            self.show_error("Please enter a valid date (YYYY-MM-DD).")
            self.ent_start_date.focus_set()
            return

        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            self.show_error("Date must be in YYYY-MM-DD format (e.g. 2026-10-15).")
            self.ent_start_date.focus_set()
            return

        try:
            t_s = datetime.strptime(start_time, "%H:%M")
        except ValueError:
            self.show_error("Start time must be in HH:MM format (e.g. 09:30).")
            self.ent_start_time.focus_set()
            return

        try:
            t_e = datetime.strptime(end_time, "%H:%M")
        except ValueError:
            self.show_error("End time must be in HH:MM format (e.g. 10:30).")
            self.ent_end_time.focus_set()
            return

        if t_e < t_s:
            self.show_error("End time cannot be earlier than start time.")
            self.ent_end_time.focus_set()
            return

        self.clear_error()
        self.btn_submit.configure(state="disabled")

        sel_course_name = self.opt_sub.get()
        subject_id = None
        for s in self.subjects:
            if s["name"] == sel_course_name:
                subject_id = s["id"]
                break

        category = self.opt_category.get()
        payload = {
            "title": title,
            "event_type": category,
            "category": category,
            "color": self.selected_color,
            "subject_id": subject_id,
            "start_date": start_date,
            "start_time": start_time,
            "end_date": start_date,
            "end_time": end_time,
            "location": self.ent_location.get().strip(),
            "notes": self.ent_notes.get().strip(),
            "reminder": self.opt_reminder.get(),
            "recurring": self.opt_recurring.get()
        }
        if "id" in self.event_data:
            payload["id"] = self.event_data["id"]

        self.on_save(payload)
        self.destroy()


class RenameCategoryModal(BaseModal):
    """Dialog to rename an existing category."""

    def __init__(self, parent: Any, cat_id: int, current_name: str, on_save: Callable[[str], None]):
        super().__init__(parent, "Rename Category", width=400, height=280)
        self.cat_id = cat_id
        self.on_save = on_save
        colors = Theme.current()

        ctk.CTkLabel(self.content_frame, text="Category Name *", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_name = ctk.CTkEntry(
            self.content_frame,
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=36
        )
        self.ent_name.insert(0, current_name)
        self.ent_name.pack(fill="x", pady=(0, 12))
        self.ent_name.bind("<Return>", lambda e: self._save())

        self.btn_submit = ctk.CTkButton(
            self.footer_inner,
            text="Save",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            height=36,
            width=90,
            command=self._save
        )
        self.btn_submit.pack(side="right")

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
            width=80,
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=(0, 8))

    def _save(self):
        new_name = self.ent_name.get().strip()
        if not new_name:
            self.show_error("Please enter a category name.")
            return
        self.on_save(new_name)
        self.destroy()


class CategoryManagerModal(BaseModal):
    """Dialog to create, rename, recolor, and delete custom calendar event categories."""

    def __init__(self, parent: Any, on_changed: Optional[Callable[[], None]] = None):
        super().__init__(parent, "Manage Event Categories", width=480, height=560)
        self.on_changed = on_changed
        self._build_ui()

    def _build_ui(self):
        colors = Theme.current()
        self.categories = database.get_event_categories()

        ctk.CTkLabel(
            self.content_frame,
            text="Calendar Event Categories & Colors",
            font=Theme.font_subheader(),
            text_color=colors["text_primary"]
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            self.content_frame,
            text="Customize categories and pastel colors. Existing events update automatically.",
            font=Theme.font_small(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 10))

        # Scrollable list of current categories
        self.cat_scroll = ctk.CTkScrollableFrame(self.content_frame, height=220, fg_color=colors["bg_card_secondary"], corner_radius=10)
        self.cat_scroll.pack(fill="x", pady=(0, 12))
        self._render_category_list()

        # Add New Category Card
        add_box = ctk.CTkFrame(self.content_frame, fg_color=colors["bg_card"], corner_radius=10, border_width=1, border_color=colors["border"])
        add_box.pack(fill="x", pady=(0, 8))
        a_inner = ctk.CTkFrame(add_box, fg_color="transparent")
        a_inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(a_inner, text="Add New Category", font=Theme.font_body_bold(), text_color=colors["text_primary"]).pack(anchor="w", pady=(0, 6))

        row1 = ctk.CTkFrame(a_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))

        self.ent_new_cat = ctk.CTkEntry(
            row1,
            placeholder_text="Category name (e.g. Lab, Club, Work)",
            font=Theme.font_body(),
            fg_color=colors["input_bg"],
            border_color=colors["input_border"],
            height=34
        )
        self.ent_new_cat.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.new_cat_color = "#FF7597"
        self.btn_new_color = ctk.CTkButton(
            row1,
            text="",
            width=34,
            height=34,
            corner_radius=17,
            fg_color=self.new_cat_color,
            hover_color=self.new_cat_color,
            command=self._pick_new_category_color
        )
        self.btn_new_color.pack(side="left", padx=(0, 8))

        btn_add = ctk.CTkButton(
            row1,
            text="Add",
            font=Theme.font_body_bold(),
            width=65,
            height=34,
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            command=self._add_category
        )
        btn_add.pack(side="left")

        # Quick pastel swatches for new category
        swatch_row = ctk.CTkFrame(a_inner, fg_color="transparent")
        swatch_row.pack(fill="x")
        for col in PASTEL_SWATCHES[:8]:
            ctk.CTkButton(
                swatch_row,
                text="",
                width=20,
                height=20,
                corner_radius=10,
                fg_color=col,
                hover_color=col,
                command=lambda c=col: self._set_new_cat_color(c)
            ).pack(side="left", padx=2)

        # Footer button: Close
        btn_done = ctk.CTkButton(
            self.footer_inner,
            text="Done",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            height=36,
            width=100,
            command=self._finish
        )
        btn_done.pack(side="right")

    def _render_category_list(self):
        colors = Theme.current()
        for child in self.cat_scroll.winfo_children():
            child.destroy()

        self.categories = database.get_event_categories()
        for cat in self.categories:
            row = ctk.CTkFrame(self.cat_scroll, fg_color=colors["bg_card"], corner_radius=8, height=36)
            row.pack(fill="x", pady=2)

            r_in = ctk.CTkFrame(row, fg_color="transparent")
            r_in.pack(fill="x", padx=8, pady=4)

            # Color circle
            ctk.CTkLabel(
                r_in,
                text="",
                width=16,
                height=16,
                corner_radius=8,
                fg_color=cat["color"]
            ).pack(side="left", padx=(0, 8))

            # Name
            ctk.CTkLabel(
                r_in,
                text=cat["name"],
                font=Theme.font_body_bold(),
                text_color=colors["text_primary"],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            # Delete button (only if > 1 category)
            if len(self.categories) > 1:
                btn_del = ctk.CTkButton(
                    r_in,
                    text="",
                    image=icons.get_icon("trash", size=13, color="#D94161"),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card_secondary"],
                    command=lambda cid=cat["id"]: self._delete_category(cid)
                )
                btn_del.pack(side="right", padx=(2, 0))

            # Recolor button
            btn_col = ctk.CTkButton(
                r_in,
                text="",
                image=icons.get_icon("palette", size=13, color=colors["text_secondary"]),
                width=26,
                height=26,
                fg_color="transparent",
                hover_color=colors["bg_card_secondary"],
                command=lambda c=cat: self._recolor_category(c)
            )
            btn_col.pack(side="right", padx=(2, 0))

            # Rename button
            btn_ren = ctk.CTkButton(
                r_in,
                text="",
                image=icons.get_icon("edit", size=13, color=colors["text_secondary"]),
                width=26,
                height=26,
                fg_color="transparent",
                hover_color=colors["bg_card_secondary"],
                command=lambda c=cat: self._rename_category(c)
            )
            btn_ren.pack(side="right")

    def _set_new_cat_color(self, hex_col: str):
        self.new_cat_color = hex_col
        self.btn_new_color.configure(fg_color=hex_col, hover_color=hex_col)

    def _pick_new_category_color(self):
        res = colorchooser.askcolor(color=self.new_cat_color, title="Select Category Color", parent=self)
        if res and res[1]:
            self._set_new_cat_color(res[1])

    def _recolor_category(self, cat: dict):
        res = colorchooser.askcolor(color=cat["color"], title=f"Select Color for {cat['name']}", parent=self)
        if res and res[1]:
            database.update_event_category(cat["id"], cat["name"], res[1])
            self._render_category_list()
            if self.on_changed:
                self.on_changed()

    def _rename_category(self, cat: dict):
        def on_renamed(new_name: str):
            database.rename_event_category(cat["id"], new_name)
            self._render_category_list()
            if self.on_changed:
                self.on_changed()

        RenameCategoryModal(self, cat["id"], cat["name"], on_renamed)

    def _add_category(self):
        name = self.ent_new_cat.get().strip()
        if not name:
            return
        database.add_event_category(name, self.new_cat_color)
        self.ent_new_cat.delete(0, "end")
        self._render_category_list()
        if self.on_changed:
            self.on_changed()

    def _delete_category(self, cat_id: int):
        database.delete_event_category(cat_id)
        self._render_category_list()
        if self.on_changed:
            self.on_changed()

    def _finish(self):
        if self.on_changed:
            self.on_changed()
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

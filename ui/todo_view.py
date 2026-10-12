"""
ui/todo_view.py - Modern Daily To-Do List View for Chiikawa Study Planner
Manages tasks, categories, priorities, due dates, and status filters.
Refactored with PageHeader, Card, PrimaryButton, GhostButton, StyledEntry, StyledCheckBox, and EmptyState.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date
from typing import Optional, Any
from theme import Theme
import database
import icons
from ui.components.widgets import (
    PageHeader,
    Card,
    PrimaryButton,
    GhostButton,
    StyledEntry,
    StyledCheckBox,
    EmptyState
)
from ui.components.modal import TaskModal
from ui.components.toast import ToastNotification


class TodoView(ctk.CTkFrame):
    """Daily To-Do List manager with categories, priorities, due dates, and filters."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self.active_tab = "Daily Tasks"
        self.current_filter_status = "all"
        self.current_category = "All"
        self.current_priority = "All"
        self.search_term = ""

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        # 1. Page Header with Tab Switcher & Action Button
        self.header = PageHeader(
            self,
            title="Daily Tasks",
            subtitle="Organize your daily studies, assignments, and personal goals."
        )
        self.header.pack(fill="x", padx=24, pady=(20, 14))

        ic_plus = icons.get_icon("plus", size=16, color="#FFFFFF")
        btn_new_task = PrimaryButton(
            self.header.actions_container,
            text="New Task",
            image=ic_plus,
            command=self._open_new_task_modal,
            width=136,
            height=Theme.BTN_HEIGHT
        )
        btn_new_task.pack(side="right")

        self.seg_tab = ctk.CTkSegmentedButton(
            self.header.actions_container,
            values=["Daily Tasks", "General Tasks"],
            font=Theme.font_body(),
            height=Theme.BTN_HEIGHT,
            corner_radius=10,
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card"],
            unselected_hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            command=self._on_tab_change
        )
        self.seg_tab.set("Daily Tasks")
        self.seg_tab.pack(side="right", padx=(0, 12))

        # 2. Filter & Search Toolbar Card
        toolbar = Card(
            self,
            corner_radius=Theme.RADIUS_MD,
            hoverable=False
        )
        toolbar.pack(fill="x", padx=24, pady=(0, 14))

        tb_inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        tb_inner.pack(fill="x", padx=16, pady=12)

        # Status Segmented Button (All / Active / Completed)
        self.seg_status = ctk.CTkSegmentedButton(
            tb_inner,
            values=["All", "Active", "Completed"],
            font=Theme.font_body(),
            height=36,
            corner_radius=10,
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card_secondary"],
            unselected_hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            command=self._on_status_change
        )
        self.seg_status.set("All")
        self.seg_status.pack(side="left", padx=(0, 14))

        # Category Filter
        ctk.CTkLabel(tb_inner, text="Category:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 6))
        self.opt_category = ctk.CTkOptionMenu(
            tb_inner,
            values=["All", "Study", "Homework", "Exam Prep", "Reading", "Personal", "Project"],
            font=Theme.font_body(),
            width=115,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            command=self._on_filter_change
        )
        self.opt_category.set("All")
        self.opt_category.pack(side="left", padx=(0, 14))

        # Priority Filter
        ctk.CTkLabel(tb_inner, text="Priority:", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(side="left", padx=(0, 6))
        self.opt_priority = ctk.CTkOptionMenu(
            tb_inner,
            values=["All", "High", "Medium", "Low"],
            font=Theme.font_body(),
            width=100,
            height=36,
            corner_radius=10,
            fg_color=colors["bg_card_secondary"],
            text_color=colors["text_primary"],
            button_color=colors["bg_card_secondary"],
            button_hover_color=colors["bg_sidebar_hover"],
            command=self._on_filter_change
        )
        self.opt_priority.set("All")
        self.opt_priority.pack(side="left", padx=(0, 14))

        # Search Bar
        self.ent_search = StyledEntry(
            tb_inner,
            placeholder_text="Search tasks...",
            width=190,
            height=36
        )
        self.ent_search.pack(side="right")
        self.ent_search.bind("<KeyRelease>", lambda e: self._on_search())

        # 3. Scrollable Task Cards Container
        self.tasks_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.tasks_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 10))

        # 4. Footer Status bar
        self.footer = ctk.CTkFrame(self, fg_color="transparent", height=32)
        self.footer.pack(fill="x", padx=26, pady=(0, 14))

        self.lbl_stats = ctk.CTkLabel(
            self.footer,
            text="",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        )
        self.lbl_stats.pack(side="left")

    def _on_tab_change(self, tab_name: str):
        if "General" in tab_name or tab_name == "Tasks":
            self.active_tab = "General Tasks"
            self.header.lbl_title.configure(text="General Tasks")
            self.header.lbl_subtitle.configure(text="One-time reminders, errands, and tasks that do not appear as daily tasks.")
        else:
            self.active_tab = "Daily Tasks"
            self.header.lbl_title.configure(text="Daily Tasks")
            self.header.lbl_subtitle.configure(text="Organize your daily studies, assignments, and personal goals.")
        self.refresh()

    def _on_status_change(self, value: str):
        self.current_filter_status = value.lower()
        self.refresh()

    def _on_filter_change(self, _=None):
        self.current_category = self.opt_category.get()
        self.current_priority = self.opt_priority.get()
        self.refresh()

    def _on_search(self):
        self.search_term = self.ent_search.get().strip()
        self.refresh()

    def refresh(self):
        colors = Theme.current()
        for child in self.tasks_scroll.winfo_children():
            child.destroy()

        active_type = "general" if self.active_tab == "General Tasks" else "daily"
        tasks = database.get_tasks(
            filter_status=self.current_filter_status,
            category=self.current_category,
            priority=self.current_priority,
            search_query=self.search_term or None,
            task_type=active_type
        )

        all_tasks = database.get_tasks(task_type=active_type)
        total_count = len(all_tasks)
        active_count = sum(1 for t in all_tasks if not t["completed"])
        completed_count = total_count - active_count
        self.lbl_stats.configure(
            text=f"{self.active_tab} Total: {total_count}  •  Pending: {active_count}  •  Completed: {completed_count}"
        )

        if not tasks:
            if self.active_tab == "General Tasks":
                empty_title = "No general tasks found"
                empty_desc = "Add one-time reminders, errands, and to-dos that don't need daily recurrence."
            else:
                empty_title = "No daily tasks found"
                empty_desc = "No daily tasks match your current criteria.\nCreate a task to get moving forward!"
            empty = EmptyState(
                self.tasks_scroll,
                title=empty_title,
                description=empty_desc,
                mascot_name="passed",
                action_text="Add a Task",
                action_command=self._open_new_task_modal
            )
            empty.pack(fill="x", pady=24)
            return

        for task in tasks:
            self._render_task_card(task)

    def _render_task_card(self, task: dict):
        colors = Theme.current()
        task_id = task["id"]
        is_done = bool(task["completed"])

        card = Card(
            self.tasks_scroll,
            fg_color=colors["bg_card_secondary"] if is_done else colors["bg_card"],
            corner_radius=Theme.RADIUS_MD,
            border_width=1,
            border_color=colors["border_subtle"],
            hoverable=True
        )
        card.pack(fill="x", pady=4)

        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="both", expand=True, padx=16, pady=12)

        # Left side: Checkbox + details
        left_box = ctk.CTkFrame(card_inner, fg_color="transparent")
        left_box.pack(side="left", fill="both", expand=True)

        top_line = ctk.CTkFrame(left_box, fg_color="transparent")
        top_line.pack(fill="x", anchor="w")

        var_chk = tk.BooleanVar(value=is_done)
        chk = StyledCheckBox(
            top_line,
            text="",
            variable=var_chk,
            command=lambda tid=task_id, v=var_chk: self._toggle_task(tid, v.get())
        )
        chk.pack(side="left", padx=(0, 12))

        title_color = colors["text_muted"] if is_done else colors["text_primary"]
        lbl_title = ctk.CTkLabel(
            top_line,
            text=task["title"],
            font=Theme.font_body_bold() if not is_done else Theme.font_body(),
            text_color=title_color,
            anchor="w"
        )
        lbl_title.pack(side="left", fill="x", expand=True)

        # Badges row
        badges_line = ctk.CTkFrame(left_box, fg_color="transparent")
        badges_line.pack(fill="x", anchor="w", padx=(34, 0), pady=(4, 0))

        if task.get("subject_name"):
            ctk.CTkLabel(
                badges_line,
                text=task['subject_name'],
                font=Theme.font_tag(),
                text_color=colors["text_primary"],
                fg_color=colors["bg_card_secondary"],
                corner_radius=6,
                padx=8,
                pady=2
            ).pack(side="left", padx=(0, 8))

        cat = task.get("category", "Study")
        ctk.CTkLabel(
            badges_line,
            text=cat,
            font=Theme.font_tag(),
            text_color=colors["text_secondary"],
            fg_color=colors["bg_card_secondary"],
            corner_radius=6,
            padx=8,
            pady=2
        ).pack(side="left", padx=(0, 8))

        prio = task.get("priority", "Medium")
        prio_color = colors["accent_yellow"]
        if prio == "High":
            prio_color = colors["accent_pink"]
        elif prio == "Low":
            prio_color = colors["accent_mint"]

        ctk.CTkLabel(
            badges_line,
            text=f"● {prio}",
            font=Theme.font_tag(),
            text_color=colors["text_primary"],
            fg_color=colors["bg_card_secondary"],
            corner_radius=6,
            padx=8,
            pady=2
        ).pack(side="left", padx=(0, 8))

        due_d = task.get("due_date")
        if due_d:
            today_str = date.today().isoformat()
            if due_d < today_str and not is_done:
                due_label = f"Overdue ({due_d})"
                due_color = colors["priority_high_bg"]
                due_fg = colors["priority_high_fg"]
            elif due_d == today_str:
                due_label = f"Due Today"
                due_color = colors["priority_med_bg"]
                due_fg = colors["priority_med_fg"]
            else:
                due_label = f"Due {due_d}"
                due_color = colors["bg_card_secondary"]
                due_fg = colors["text_secondary"]

            ctk.CTkLabel(
                badges_line,
                text=due_label,
                font=Theme.font_tag(),
                text_color=due_fg,
                fg_color=due_color,
                corner_radius=6,
                padx=8,
                pady=2
            ).pack(side="left")

        desc = task.get("description", "").strip()
        if desc:
            ctk.CTkLabel(
                left_box,
                text=desc,
                font=Theme.font_body(),
                text_color=colors["text_secondary"],
                anchor="w",
                wraplength=520,
                justify="left"
            ).pack(anchor="w", padx=(34, 0), pady=(4, 0))

        # Right side: Vector-styled Edit & Delete buttons
        right_box = ctk.CTkFrame(card_inner, fg_color="transparent")
        right_box.pack(side="right", padx=(12, 0))

        ic_edit = icons.get_icon("edit", size=15, color=colors["text_secondary"])
        btn_edit = GhostButton(
            right_box,
            text="",
            image=ic_edit,
            width=36,
            height=36,
            command=lambda t=task: self._open_edit_task_modal(t)
        )
        btn_edit.pack(side="left", padx=(0, 6))

        ic_trash = icons.get_icon("trash", size=15, color=colors["priority_high_fg"])
        btn_del = GhostButton(
            right_box,
            text="",
            image=ic_trash,
            width=36,
            height=36,
            command=lambda tid=task_id: self._delete_task(tid)
        )
        btn_del.pack(side="left")

    def _toggle_task(self, task_id: int, new_val: bool):
        database.toggle_task_completed(task_id, new_val)
        self.refresh()

    def _delete_task(self, task_id: int):
        database.delete_task(task_id)
        ToastNotification.show(self.winfo_toplevel(), "Task deleted.", color_theme="blue")
        self.refresh()

    def _open_new_task_modal(self):
        default_type = "general" if self.active_tab == "General Tasks" else "daily"
        def on_saved(data):
            database.add_task(
                title=data["title"],
                description=data["description"],
                subject_id=data["subject_id"],
                category=data["category"],
                priority=data["priority"],
                due_date=data["due_date"],
                due_time=data["due_time"],
                task_type=data.get("task_type", default_type)
            )
            ToastNotification.show(self.winfo_toplevel(), "Task created.", color_theme="pink")
            self.refresh()

        TaskModal(self.winfo_toplevel(), on_saved, default_task_type=default_type)

    def _open_edit_task_modal(self, task: dict):
        def on_saved(data):
            database.update_task(
                task_id=data["id"],
                title=data["title"],
                description=data["description"],
                subject_id=data["subject_id"],
                category=data["category"],
                priority=data["priority"],
                due_date=data["due_date"],
                due_time=data["due_time"],
                task_type=data.get("task_type", task.get("task_type", "daily"))
            )
            ToastNotification.show(self.winfo_toplevel(), "Task updated.", color_theme="pink")
            self.refresh()

        TaskModal(self.winfo_toplevel(), on_saved, task_data=task, default_task_type=task.get("task_type", "daily"))

"""
ui/study_planner_view.py - Modern Study Planner View for Chiikawa Study Planner
Organizes academic courses, exam/assignment countdowns, and study session logs.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date, timedelta
from typing import Optional, Any
from theme import Theme
import database
import icons
from ui.components.modal import SubjectModal, EventModal, SessionModal
from ui.components.toast import ToastNotification


class StudyPlannerView(ctk.CTkFrame):
    """Study Planner with Course management, Exam/Assignment countdowns, and Study logs."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self.active_tab = "Courses"

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
            text="Study Planner",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Manage your academic courses, exam countdowns, and study logs.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        # Tab switcher
        self.seg_tab = ctk.CTkSegmentedButton(
            header,
            values=["Courses", "Exams & Deadlines", "Study Logs"],
            font=Theme.font_body(),
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card"],
            text_color=colors["text_primary"],
            command=self._on_tab_change
        )
        self.seg_tab.set("Courses")
        self.seg_tab.pack(side="right")

        # Main Scrollable Container
        self.content_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
        )
        self.content_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def _on_tab_change(self, tab_name: str):
        self.active_tab = tab_name
        self.refresh()

    def refresh(self):
        for child in self.content_scroll.winfo_children():
            child.destroy()

        if self.active_tab == "Courses":
            self._render_subjects()
        elif self.active_tab == "Exams & Deadlines":
            self._render_exams()
        else:
            self._render_logs()

    # -------------------------------------------------------------
    # 1. Subjects Manager
    # -------------------------------------------------------------
    def _render_subjects(self):
        colors = Theme.current()

        top_row = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            top_row,
            text="Active Academic Courses",
            font=Theme.font_header(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        ic_plus = icons.get_icon("plus", size=14, color="#FFFFFF")
        btn_add = ctk.CTkButton(
            top_row,
            text=" Add Course",
            image=ic_plus,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=34,
            command=self._open_add_subject_modal
        )
        btn_add.pack(side="right")

        subjects = database.get_all_subjects()
        sessions = database.get_study_sessions(limit=500)

        subject_minutes = {}
        for s in sessions:
            sid = s.get("subject_id")
            if sid:
                subject_minutes[sid] = subject_minutes.get(sid, 0) + s["duration_minutes"]

        if not subjects:
            ctk.CTkLabel(
                self.content_scroll,
                text="No courses added yet. Click 'Add Course' to begin organizing your subjects.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(pady=30)
            return

        grid_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        grid_frame.pack(fill="x")
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        for i, sub in enumerate(subjects):
            row = i // 2
            col = i % 2

            card = ctk.CTkFrame(
                grid_frame,
                fg_color=colors["bg_card"],
                corner_radius=14,
                border_width=1,
                border_color=colors["border"]
            )
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

            card_inner = ctk.CTkFrame(card, fg_color="transparent")
            card_inner.pack(fill="both", expand=True, padx=16, pady=14)

            # Header
            h_line = ctk.CTkFrame(card_inner, fg_color="transparent")
            h_line.pack(fill="x")

            sub_col = sub.get("color", colors["accent_pink"])

            # Left color pill
            color_dot = ctk.CTkFrame(h_line, width=12, height=12, corner_radius=6, fg_color=sub_col)
            color_dot.pack(side="left", padx=(0, 10))

            t_box = ctk.CTkFrame(h_line, fg_color="transparent")
            t_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(t_box, text=sub["name"], font=Theme.font_header(), text_color=colors["text_primary"], anchor="w").pack(anchor="w")

            # Actions with vector icons
            ic_edit = icons.get_icon("edit", size=13, color=colors["text_secondary"])
            btn_edit = ctk.CTkButton(
                h_line,
                text="",
                image=ic_edit,
                width=28,
                height=28,
                fg_color="transparent",
                hover_color=colors["bg_card_secondary"],
                command=lambda s=sub: self._open_edit_subject_modal(s)
            )
            btn_edit.pack(side="right", padx=(4, 0))

            ic_trash = icons.get_icon("trash", size=13, color="#D94161")
            btn_del = ctk.CTkButton(
                h_line,
                text="",
                image=ic_trash,
                width=28,
                height=28,
                fg_color="transparent",
                hover_color=colors["bg_card_secondary"],
                command=lambda sid=sub["id"]: self._delete_subject(sid)
            )
            btn_del.pack(side="right")

            desc = sub.get("description", "").strip() or "No course description provided."
            ctk.CTkLabel(card_inner, text=desc, font=Theme.font_small(), text_color=colors["text_secondary"], wraplength=320, justify="left").pack(anchor="w", pady=(8, 10))

            mins = subject_minutes.get(sub["id"], 0)
            hrs = mins // 60
            rmins = mins % 60
            time_txt = f"{hrs}h {rmins}m" if hrs > 0 else f"{mins}m"

            ftr_row = ctk.CTkFrame(card_inner, fg_color="transparent")
            ftr_row.pack(fill="x")

            ctk.CTkLabel(
                ftr_row,
                text=f"Total Study: {time_txt}",
                font=Theme.font_tag(),
                text_color=colors["text_primary"],
                fg_color=colors["bg_card_secondary"],
                corner_radius=5,
                padx=8,
                pady=2
            ).pack(side="left")

    # -------------------------------------------------------------
    # 2. Exams & Deadlines Countdown
    # -------------------------------------------------------------
    def _render_exams(self):
        colors = Theme.current()

        top_row = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            top_row,
            text="Exams, Assignments & Deadlines",
            font=Theme.font_header(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        ic_plus = icons.get_icon("plus", size=14, color="#FFFFFF")
        btn_add = ctk.CTkButton(
            top_row,
            text=" Add Exam / Deadline",
            image=ic_plus,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=34,
            command=self._open_add_exam_modal
        )
        btn_add.pack(side="right")

        events = database.get_calendar_events()
        academic_events = [e for e in events if e.get("event_type") in ("Exam", "Assignment", "Deadline")]

        if not academic_events:
            ctk.CTkLabel(
                self.content_scroll,
                text="No upcoming exams or deadlines logged.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(pady=30)
            return

        for ev in academic_events:
            card = ctk.CTkFrame(
                self.content_scroll,
                fg_color=colors["bg_card"],
                corner_radius=12,
                border_width=1,
                border_color=colors["border"]
            )
            card.pack(fill="x", pady=4)

            card_inner = ctk.CTkFrame(card, fg_color="transparent")
            card_inner.pack(fill="both", expand=True, padx=16, pady=12)

            left_box = ctk.CTkFrame(card_inner, fg_color="transparent")
            left_box.pack(side="left", fill="both", expand=True)

            d_str = ev.get("start_date", "")
            try:
                target_d = datetime.strptime(d_str, "%Y-%m-%d").date()
                diff = (target_d - date.today()).days
                if diff < 0:
                    badge_txt = f"Passed ({abs(diff)}d ago)"
                    badge_bg = colors["border"]
                    badge_fg = colors["text_secondary"]
                elif diff == 0:
                    badge_txt = "Due Today"
                    badge_bg = colors["accent_pink"]
                    badge_fg = "#FFFFFF"
                elif diff == 1:
                    badge_txt = "Tomorrow"
                    badge_bg = colors["accent_yellow"]
                    badge_fg = colors["text_primary"]
                else:
                    badge_txt = f"In {diff} days"
                    badge_bg = colors["accent_blue"]
                    badge_fg = colors["text_primary"]
            except Exception:
                badge_txt = d_str
                badge_bg = colors["bg_card_secondary"]
                badge_fg = colors["text_primary"]

            h_line = ctk.CTkFrame(left_box, fg_color="transparent")
            h_line.pack(fill="x")

            ctk.CTkLabel(
                h_line,
                text=badge_txt,
                font=Theme.font_tag(),
                text_color=badge_fg,
                fg_color=badge_bg,
                corner_radius=5,
                padx=8,
                pady=2
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                h_line,
                text=f"[{ev.get('event_type')}] {ev['title']}",
                font=Theme.font_body_bold(),
                text_color=colors["text_primary"]
            ).pack(side="left")

            sub_name = ev.get("subject_name", "General")
            notes_str = f" • Notes: {ev['notes']}" if ev.get("notes") else ""
            ctk.CTkLabel(
                left_box,
                text=f"Course: {sub_name}  •  Date: {ev.get('start_date')} at {ev.get('start_time')}{notes_str}",
                font=Theme.font_small(),
                text_color=colors["text_secondary"]
            ).pack(anchor="w", pady=(4, 0))

            ic_trash = icons.get_icon("trash", size=13, color="#D94161")
            btn_del = ctk.CTkButton(
                card_inner,
                text="",
                image=ic_trash,
                width=28,
                height=28,
                fg_color="transparent",
                hover_color=colors["bg_card_secondary"],
                command=lambda eid=ev["id"]: self._delete_event(eid)
            )
            btn_del.pack(side="right")

    # -------------------------------------------------------------
    # 3. Study Logs
    # -------------------------------------------------------------
    def _render_logs(self):
        colors = Theme.current()

        top_row = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            top_row,
            text="Study Sessions & Focus Logs",
            font=Theme.font_header(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        ic_plus = icons.get_icon("plus", size=14, color="#FFFFFF")
        btn_log = ctk.CTkButton(
            top_row,
            text=" Log Study Session",
            image=ic_plus,
            compound="left",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=10,
            height=34,
            command=self._open_manual_log_dialog
        )
        btn_log.pack(side="right")

        sessions = database.get_study_sessions(limit=50)
        if not sessions:
            ctk.CTkLabel(
                self.content_scroll,
                text="No study sessions logged yet. Complete a Pomodoro session or log one manually.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(pady=30)
            return

        for ss in sessions:
            card = ctk.CTkFrame(
                self.content_scroll,
                fg_color=colors["bg_card"],
                corner_radius=12,
                border_width=1,
                border_color=colors["border_subtle"]
            )
            card.pack(fill="x", pady=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(
                left,
                text=f"{ss['duration_minutes']} min  •  {ss.get('topic', 'Study')}",
                font=Theme.font_body_bold(),
                text_color=colors["text_primary"]
            ).pack(anchor="w")

            sub_txt = ss.get("subject_name") or "General"
            notes_txt = f" - '{ss['notes']}'" if ss.get("notes") else ""
            ctk.CTkLabel(
                left,
                text=f"Course: {sub_txt}  •  Date: {ss['date']}  •  Type: {ss.get('session_type', 'Pomodoro')}{notes_txt}",
                font=Theme.font_small(),
                text_color=colors["text_secondary"]
            ).pack(anchor="w", pady=(2, 0))

    # Modal Handlers
    def _open_add_subject_modal(self):
        def on_saved(data):
            database.add_subject(
                name=data["name"],
                color=data["color"],
                icon=data["icon"],
                description=data["description"]
            )
            ToastNotification.show(self.winfo_toplevel(), "Course added.", color_theme="pink")
            self.refresh()

        SubjectModal(self.winfo_toplevel(), on_saved)

    def _open_edit_subject_modal(self, sub: dict):
        def on_saved(data):
            database.update_subject(
                subject_id=data["id"],
                name=data["name"],
                color=data["color"],
                icon=data["icon"],
                description=data["description"]
            )
            ToastNotification.show(self.winfo_toplevel(), "Course updated.", color_theme="pink")
            self.refresh()

        SubjectModal(self.winfo_toplevel(), on_saved, subject_data=sub)

    def _delete_subject(self, sub_id: int):
        database.delete_subject(sub_id)
        ToastNotification.show(self.winfo_toplevel(), "Course deleted.", color_theme="blue")
        self.refresh()

    def _open_add_exam_modal(self):
        def on_saved(data):
            database.add_calendar_event(
                title=data["title"],
                event_type=data["event_type"],
                subject_id=data["subject_id"],
                start_date=data["start_date"],
                start_time=data["start_time"],
                end_date=data["end_date"],
                end_time=data["end_time"],
                notes=data["notes"]
            )
            ToastNotification.show(self.winfo_toplevel(), "Deadline scheduled.", color_theme="pink")
            self.refresh()

        EventModal(self.winfo_toplevel(), on_saved)

    def _delete_event(self, event_id: int):
        database.delete_calendar_event(event_id)
        ToastNotification.show(self.winfo_toplevel(), "Event removed.", color_theme="blue")
        self.refresh()

    def _open_manual_log_dialog(self):
        def on_saved(data):
            database.log_study_session(
                subject_id=data["subject_id"],
                topic=data["topic"],
                duration_minutes=data["duration_minutes"],
                session_type="Manual",
                notes=data.get("notes", "")
            )
            ToastNotification.show(self.winfo_toplevel(), "Session logged.", color_theme="mint")
            self.refresh()

        SessionModal(self.winfo_toplevel(), on_saved)

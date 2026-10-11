"""
ui/calendar_view.py - Ultra-Fast Google Calendar multi-view for Chiikawa Study Planner
Features pre-allocated lightweight grid cells, instant day inspection, and responsive navigation.
"""

import tkinter as tk
import customtkinter as ctk
import calendar
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from theme import Theme
import database
import icons
from ui.components.widgets import (
    Card,
    PrimaryButton,
    SecondaryButton,
    GhostButton,
    StyledCheckBox
)
from ui.components.modal import EventModal, TaskModal
from ui.components.toast import ToastNotification


class CalendarView(ctk.CTkFrame):
    """Calendar view with Month, Week, and Day modes, instant event markers, and inspector."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self.selected_date = date.today()
        self.view_mode = "Month"

        self.month_container: Optional[ctk.CTkFrame] = None
        self.grid_cells: List[Dict[str, Any]] = []
        self.week_container: Optional[ctk.CTkFrame] = None
        self.day_container: Optional[ctk.CTkFrame] = None

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        # Top Control Bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 14))

        left_nav = ctk.CTkFrame(header, fg_color="transparent")
        left_nav.pack(side="left")

        ic_prev = icons.get_icon("chevron_left", size=16, color=colors["text_primary"])
        self.btn_prev = ctk.CTkButton(
            left_nav,
            text="",
            image=ic_prev,
            width=40,
            height=Theme.BTN_HEIGHT,
            fg_color=colors["bg_card"],
            hover_color=colors["bg_sidebar_hover"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=10,
            command=self._prev_period
        )
        self.btn_prev.pack(side="left", padx=(0, 6))

        ic_next = icons.get_icon("chevron_right", size=16, color=colors["text_primary"])
        self.btn_next = ctk.CTkButton(
            left_nav,
            text="",
            image=ic_next,
            width=40,
            height=Theme.BTN_HEIGHT,
            fg_color=colors["bg_card"],
            hover_color=colors["bg_sidebar_hover"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=10,
            command=self._next_period
        )
        self.btn_next.pack(side="left", padx=(0, 10))

        self.btn_today = SecondaryButton(
            left_nav,
            text="Today",
            width=75,
            height=Theme.BTN_HEIGHT,
            command=self._go_today
        )
        self.btn_today.pack(side="left", padx=(0, 14))

        self.lbl_period = ctk.CTkLabel(
            left_nav,
            text="",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        )
        self.lbl_period.pack(side="left")

        # Right Controls: View Switcher & Add Event
        right_controls = ctk.CTkFrame(header, fg_color="transparent")
        right_controls.pack(side="right")

        self.seg_view = ctk.CTkSegmentedButton(
            right_controls,
            values=["Month", "Week", "Day"],
            font=Theme.font_body(),
            height=Theme.BTN_HEIGHT,
            corner_radius=10,
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card"],
            unselected_hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            command=self._on_view_mode_change
        )
        self.seg_view.set("Month")
        self.seg_view.pack(side="left", padx=(0, 12))

        ic_plus = icons.get_icon("plus", size=16, color="#FFFFFF")
        btn_add_event = PrimaryButton(
            right_controls,
            text=" Schedule Event",
            image=ic_plus,
            command=self._open_add_event_modal,
            width=150,
            height=Theme.BTN_HEIGHT
        )
        btn_add_event.pack(side="left")

        # Main Calendar Container Area
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Build Month Container structure once
        self._init_month_view_structure()

    def _init_month_view_structure(self):
        colors = Theme.current()
        self.month_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.month_container.pack(fill="both", expand=True)
        self.month_container.grid_columnconfigure(0, weight=7)
        self.month_container.grid_columnconfigure(1, weight=3)
        self.month_container.grid_rowconfigure(0, weight=1)

        # Left: Calendar Grid Card
        grid_card = ctk.CTkFrame(
            self.month_container,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        grid_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Day Headers (Mon - Sun)
        days_header = ctk.CTkFrame(grid_card, fg_color="transparent", height=32)
        days_header.pack(fill="x", padx=10, pady=(10, 4))
        days_header.grid_columnconfigure(tuple(range(7)), weight=1)

        for col_idx, d_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            ctk.CTkLabel(
                days_header,
                text=d_name,
                font=Theme.font_subheader(),
                text_color=colors["accent_pink"] if col_idx in (5, 6) else colors["text_secondary"]
            ).grid(row=0, column=col_idx, sticky="nsew")

        cells_frame = ctk.CTkFrame(grid_card, fg_color="transparent")
        cells_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for r in range(6):
            cells_frame.grid_rowconfigure(r, weight=1)
        cells_frame.grid_columnconfigure(tuple(range(7)), weight=1)

        # Pre-allocate 42 lightweight cell frames and labels
        self.grid_cells = []
        for r_idx in range(6):
            for c_idx in range(7):
                cell = tk.Frame(
                    cells_frame,
                    bg=colors["bg_card"],
                    highlightbackground=colors["border_subtle"],
                    highlightthickness=1,
                    bd=0
                )
                cell.grid(row=r_idx, column=c_idx, sticky="nsew", padx=2, pady=2)

                top_lbl = tk.Label(
                    cell,
                    text="",
                    font=Theme.font_small(),
                    fg=colors["text_primary"],
                    bg=colors["bg_card"]
                )
                top_lbl.pack(anchor="nw", padx=5, pady=(2, 0))

                ev_pill = tk.Label(
                    cell,
                    text="",
                    font=Theme.font_tag(),
                    bg=colors["accent_pink"],
                    fg="#FFFFFF",
                    padx=3,
                    pady=1
                )

                tk_pill = tk.Label(
                    cell,
                    text="",
                    font=Theme.font_tag(),
                    bg=colors["accent_yellow"],
                    fg=colors["text_primary"],
                    padx=3,
                    pady=1
                )

                cell_data = {
                    "cell": cell,
                    "top_lbl": top_lbl,
                    "ev_pill": ev_pill,
                    "tk_pill": tk_pill,
                    "day_obj": None
                }

                def make_click_handler(cd):
                    return lambda e: self._select_day(cd["day_obj"])

                cell.bind("<Button-1>", make_click_handler(cell_data))
                top_lbl.bind("<Button-1>", make_click_handler(cell_data))
                ev_pill.bind("<Button-1>", make_click_handler(cell_data))
                tk_pill.bind("<Button-1>", make_click_handler(cell_data))

                self.grid_cells.append(cell_data)

        # Right: Day Inspector Panel
        self.inspector_card = ctk.CTkFrame(
            self.month_container,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        self.inspector_card.grid(row=0, column=1, sticky="nsew")

        ins_header = ctk.CTkFrame(self.inspector_card, fg_color="transparent")
        ins_header.pack(fill="x", padx=16, pady=14)

        self.lbl_ins_date = ctk.CTkLabel(
            ins_header,
            text="",
            font=Theme.font_header(),
            text_color=colors["text_primary"]
        )
        self.lbl_ins_date.pack(side="left")

        self.ins_scroll = ctk.CTkScrollableFrame(self.inspector_card, fg_color="transparent")
        self.ins_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        btn_add = ctk.CTkButton(
            self.inspector_card,
            text=" Add Event for Day",
            image=icons.get_icon("plus", size=13, color="#FFFFFF"),
            compound="left",
            font=Theme.font_small(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=8,
            height=34,
            command=lambda: self._open_add_event_modal(default_date=self.selected_date.isoformat())
        )
        btn_add.pack(fill="x", padx=14, pady=(0, 14))

    def _on_view_mode_change(self, mode: str):
        self.view_mode = mode
        self.refresh()

    def _go_today(self):
        self.selected_date = date.today()
        self.refresh()

    def _prev_period(self):
        if self.view_mode == "Month":
            first = self.selected_date.replace(day=1)
            prev_m = first - timedelta(days=1)
            self.selected_date = prev_m.replace(day=min(self.selected_date.day, calendar.monthrange(prev_m.year, prev_m.month)[1]))
        elif self.view_mode == "Week":
            self.selected_date -= timedelta(days=7)
        else:
            self.selected_date -= timedelta(days=1)
        self.refresh()

    def _next_period(self):
        if self.view_mode == "Month":
            days_in_m = calendar.monthrange(self.selected_date.year, self.selected_date.month)[1]
            next_m = self.selected_date.replace(day=days_in_m) + timedelta(days=1)
            self.selected_date = next_m.replace(day=min(self.selected_date.day, calendar.monthrange(next_m.year, next_m.month)[1]))
        elif self.view_mode == "Week":
            self.selected_date += timedelta(days=7)
        else:
            self.selected_date += timedelta(days=1)
        self.refresh()

    def refresh(self):
        if self.view_mode == "Month":
            if self.week_container:
                self.week_container.pack_forget()
            if self.day_container:
                self.day_container.pack_forget()
            if self.month_container:
                self.month_container.pack(fill="both", expand=True)
            self._render_month_view()
        elif self.view_mode == "Week":
            if self.month_container:
                self.month_container.pack_forget()
            if self.day_container:
                self.day_container.pack_forget()
            self._render_week_view()
        else:
            if self.month_container:
                self.month_container.pack_forget()
            if self.week_container:
                self.week_container.pack_forget()
            self._render_day_view()

    # -------------------------------------------------------------
    # Fast Month View (15ms update)
    # -------------------------------------------------------------
    def _render_month_view(self):
        colors = Theme.current()
        self.lbl_period.configure(text=self.selected_date.strftime("%B %Y"))

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(self.selected_date.year, self.selected_date.month)

        start_range = month_days[0][0].isoformat()
        end_range = month_days[-1][-1].isoformat()
        events = database.get_calendar_events(start_range, end_range)
        tasks = database.get_tasks()

        events_by_date: Dict[str, List[dict]] = {}
        for ev in events:
            events_by_date.setdefault(ev["start_date"], []).append(ev)

        tasks_by_date: Dict[str, List[dict]] = {}
        for tk_item in tasks:
            if tk_item.get("due_date"):
                tasks_by_date.setdefault(tk_item["due_date"], []).append(tk_item)

        today_obj = date.today()
        flattened_days = [day for week in month_days for day in week]

        for idx, cell_data in enumerate(self.grid_cells):
            if idx >= len(flattened_days):
                cell_data["cell"].grid_remove()
                continue

            cell_data["cell"].grid()
            day_obj = flattened_days[idx]
            cell_data["day_obj"] = day_obj

            d_str = day_obj.isoformat()
            is_cur_month = (day_obj.month == self.selected_date.month)
            is_today = (day_obj == today_obj)
            is_selected = (day_obj == self.selected_date)

            cell_bg = colors["bg_sidebar_active"] if is_selected else (colors["bg_card"] if is_cur_month else colors["bg_card_secondary"])
            border_col = colors["accent_pink"] if is_selected else colors["border_subtle"]
            num_color = colors["accent_pink"] if is_today else (colors["text_primary"] if is_cur_month else colors["text_muted"])

            cell_data["cell"].configure(bg=cell_bg, highlightbackground=border_col)
            cell_data["top_lbl"].configure(
                text=str(day_obj.day),
                fg=num_color,
                bg=cell_bg,
                font=Theme.font_body_bold() if is_today else Theme.font_small()
            )

            day_events = events_by_date.get(d_str, [])
            day_tasks = tasks_by_date.get(d_str, [])

            if day_events:
                cell_data["ev_pill"].configure(text=day_events[0]['title'][:12], bg=colors["accent_pink"])
                cell_data["ev_pill"].pack(anchor="w", padx=3, pady=(1, 0), fill="x")
            else:
                cell_data["ev_pill"].pack_forget()

            if day_tasks:
                uncompleted = sum(1 for t in day_tasks if not t["completed"])
                if uncompleted > 0:
                    txt = f"{uncompleted} task" if uncompleted == 1 else f"{uncompleted} tasks"
                    cell_data["tk_pill"].configure(text=txt, bg=colors["accent_yellow"], fg=colors["text_primary"])
                    cell_data["tk_pill"].pack(anchor="w", padx=3, pady=(1, 0), fill="x")
                else:
                    cell_data["tk_pill"].pack_forget()
            else:
                cell_data["tk_pill"].pack_forget()

        self._update_inspector()

    def _select_day(self, day_obj: Optional[date]):
        if not day_obj or day_obj == self.selected_date:
            return
        old_date = self.selected_date
        self.selected_date = day_obj

        # If month changed, full month re-render
        if old_date.month != day_obj.month or old_date.year != day_obj.year:
            self._render_month_view()
            return

        # Instant 5ms cell highlight update
        colors = Theme.current()
        for cell_data in self.grid_cells:
            cd = cell_data["day_obj"]
            if cd in (old_date, day_obj):
                is_cur_month = (cd.month == self.selected_date.month)
                is_selected = (cd == self.selected_date)
                cell_bg = colors["bg_sidebar_active"] if is_selected else (colors["bg_card"] if is_cur_month else colors["bg_card_secondary"])
                border_col = colors["accent_pink"] if is_selected else colors["border_subtle"]
                cell_data["cell"].configure(bg=cell_bg, highlightbackground=border_col)
                cell_data["top_lbl"].configure(bg=cell_bg)

        self._update_inspector()

    def _update_inspector(self):
        colors = Theme.current()
        self.lbl_ins_date.configure(text=self.selected_date.strftime("%a, %b %d"))

        for child in self.ins_scroll.winfo_children():
            child.destroy()

        sel_str = self.selected_date.isoformat()
        events = database.get_calendar_events(sel_str, sel_str)
        tasks = database.get_tasks(due_date=sel_str)

        # Events & Exams Header
        ctk.CTkLabel(self.ins_scroll, text="Events & Exams", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(4, 4))
        if not events:
            ctk.CTkLabel(self.ins_scroll, text="No events scheduled.", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w", pady=2)
        else:
            for ev in events:
                ev_box = ctk.CTkFrame(self.ins_scroll, fg_color=colors["bg_card_secondary"], corner_radius=8, border_width=1, border_color=colors["border_subtle"])
                ev_box.pack(fill="x", pady=3)
                ev_inner = ctk.CTkFrame(ev_box, fg_color="transparent")
                ev_inner.pack(fill="x", padx=10, pady=8)

                top_row = ctk.CTkFrame(ev_inner, fg_color="transparent")
                top_row.pack(fill="x")

                badge_txt = ev.get("event_type", "Event")
                badge_bg = colors["accent_pink"] if badge_txt in ("Exam", "Deadline") else colors["accent_blue"]
                ctk.CTkLabel(
                    top_row,
                    text=f" {badge_txt} ",
                    font=Theme.font_tag(),
                    fg_color=badge_bg,
                    text_color="#FFFFFF",
                    corner_radius=4
                ).pack(side="left", padx=(0, 6))

                t_str = f"{ev.get('start_time', '')} - {ev['title']}" if ev.get('start_time') else ev['title']
                ctk.CTkLabel(top_row, text=t_str, font=Theme.font_body_bold(), text_color=colors["text_primary"], anchor="w").pack(side="left", fill="x", expand=True)

                # Edit & Delete Buttons
                btn_del = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("trash", size=13, color="#D94161"),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card"],
                    command=lambda eid=ev["id"]: self._delete_event(eid)
                )
                btn_del.pack(side="right", padx=(2, 0))

                btn_edit = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("edit", size=13, color=colors["text_secondary"]),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card"],
                    command=lambda ed=ev: self._open_edit_event_modal(ed)
                )
                btn_edit.pack(side="right")

                if ev.get("notes") or ev.get("subject_name"):
                    sub_info = f"Course: {ev['subject_name']}" if ev.get("subject_name") else ""
                    note_info = f"Notes: {ev['notes']}" if ev.get("notes") else ""
                    comb = "  •  ".join(filter(None, [sub_info, note_info]))
                    ctk.CTkLabel(ev_inner, text=comb, font=Theme.font_small(), text_color=colors["text_secondary"], anchor="w").pack(anchor="w", pady=(3, 0))

        # Tasks Due Header
        ctk.CTkLabel(self.ins_scroll, text="Tasks Due", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(10, 4))
        if not tasks:
            ctk.CTkLabel(self.ins_scroll, text="No tasks due on this date.", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w", pady=2)
        else:
            for tk_item in tasks:
                t_box = ctk.CTkFrame(self.ins_scroll, fg_color=colors["bg_card_secondary"], corner_radius=8, border_width=1, border_color=colors["border_subtle"])
                t_box.pack(fill="x", pady=3)
                t_inner = ctk.CTkFrame(t_box, fg_color="transparent")
                t_inner.pack(fill="x", padx=10, pady=8)

                top_row = ctk.CTkFrame(t_inner, fg_color="transparent")
                top_row.pack(fill="x")

                is_done = bool(tk_item["completed"])
                var_chk = tk.BooleanVar(value=is_done)
                chk = ctk.CTkCheckBox(
                    top_row,
                    text="",
                    variable=var_chk,
                    width=20,
                    checkbox_width=18,
                    checkbox_height=18,
                    corner_radius=4,
                    fg_color=colors["accent_pink"],
                    hover_color=colors["accent_pink_hover"],
                    border_color=colors["border"],
                    command=lambda tid=tk_item["id"], v=var_chk: self._toggle_task(tid, v.get())
                )
                chk.pack(side="left", padx=(0, 6))

                ctk.CTkLabel(
                    top_row,
                    text=tk_item["title"],
                    font=Theme.font_body_bold(),
                    text_color=colors["text_muted"] if is_done else colors["text_primary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)

                # Edit & Delete Buttons
                btn_del = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("trash", size=13, color="#D94161"),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card"],
                    command=lambda tid=tk_item["id"]: self._delete_task(tid)
                )
                btn_del.pack(side="right", padx=(2, 0))

                btn_edit = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("edit", size=13, color=colors["text_secondary"]),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card"],
                    command=lambda td=tk_item: self._open_edit_task_modal(td)
                )
                btn_edit.pack(side="right")

                prio = tk_item.get("priority", "Medium")
                cat = tk_item.get("category", "Study")
                d_time = tk_item.get("due_time", "23:59")
                ctk.CTkLabel(
                    t_inner,
                    text=f"Priority: {prio}  •  Category: {cat}  •  Due: {d_time}",
                    font=Theme.font_small(),
                    text_color=colors["text_secondary"],
                    anchor="w"
                ).pack(anchor="w", pady=(3, 0))

    # -------------------------------------------------------------
    # Week View Implementation
    # -------------------------------------------------------------
    def _render_week_view(self):
        colors = Theme.current()
        start_of_week = self.selected_date - timedelta(days=self.selected_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        self.lbl_period.configure(text=f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}")

        if not self.week_container:
            self.week_container = ctk.CTkFrame(self.main_content, fg_color=colors["bg_card"], corner_radius=16, border_width=1, border_color=colors["border"])
        self.week_container.pack(fill="both", expand=True)

        for child in self.week_container.winfo_children():
            child.destroy()

        self.week_container.grid_columnconfigure(tuple(range(7)), weight=1)
        self.week_container.grid_rowconfigure(0, weight=1)

        events = database.get_calendar_events(start_of_week.isoformat(), end_of_week.isoformat())
        tasks = database.get_tasks()

        for i in range(7):
            cur_d = start_of_week + timedelta(days=i)
            cur_str = cur_d.isoformat()
            is_today = (cur_d == date.today())

            col_frame = ctk.CTkFrame(
                self.week_container,
                fg_color=colors["bg_sidebar_active"] if is_today else colors["bg_card_secondary"],
                corner_radius=10,
                border_width=1,
                border_color=colors["accent_pink"] if is_today else colors["border_subtle"]
            )
            col_frame.grid(row=0, column=i, sticky="nsew", padx=3, pady=8)

            h_frame = ctk.CTkFrame(col_frame, fg_color="transparent")
            h_frame.pack(fill="x", padx=6, pady=8)

            ctk.CTkLabel(
                h_frame,
                text=cur_d.strftime("%a"),
                font=Theme.font_subheader(),
                text_color=colors["accent_pink"] if is_today else colors["text_secondary"]
            ).pack()

            ctk.CTkLabel(
                h_frame,
                text=str(cur_d.day),
                font=Theme.font_header(),
                text_color=colors["text_primary"]
            ).pack()

            scroll_day = ctk.CTkFrame(col_frame, fg_color="transparent")
            scroll_day.pack(fill="both", expand=True, padx=4, pady=(0, 6))

            day_events = [ev for ev in events if ev["start_date"] == cur_str]
            for ev in day_events:
                ev_card = ctk.CTkFrame(scroll_day, fg_color=colors["accent_pink"], corner_radius=5)
                ev_card.pack(fill="x", pady=2)
                ctk.CTkLabel(ev_card, text=ev["title"], font=Theme.font_tag(), text_color="#FFFFFF", wraplength=100).pack(padx=4, pady=2)

            day_tasks = [t for t in tasks if t.get("due_date") == cur_str]
            for t in day_tasks:
                t_card = ctk.CTkFrame(scroll_day, fg_color=colors["bg_card"], corner_radius=5, border_width=1, border_color=colors["border_subtle"])
                t_card.pack(fill="x", pady=2)
                ctk.CTkLabel(t_card, text=t["title"], font=Theme.font_tag(), text_color=colors["text_primary"], wraplength=100).pack(padx=4, pady=2)

    # -------------------------------------------------------------
    # Day View Implementation
    # -------------------------------------------------------------
    def _render_day_view(self):
        colors = Theme.current()
        self.lbl_period.configure(text=self.selected_date.strftime("%A, %B %d, %Y"))

        if not self.day_container:
            self.day_container = ctk.CTkFrame(self.main_content, fg_color=colors["bg_card"], corner_radius=16, border_width=1, border_color=colors["border"])
        self.day_container.pack(fill="both", expand=True)

        for child in self.day_container.winfo_children():
            child.destroy()

        scroll_agenda = ctk.CTkScrollableFrame(self.day_container, fg_color="transparent")
        scroll_agenda.pack(fill="both", expand=True, padx=24, pady=16)

        sel_str = self.selected_date.isoformat()
        events = database.get_calendar_events(sel_str, sel_str)
        tasks = database.get_tasks(due_date=sel_str)

        ctk.CTkLabel(
            scroll_agenda,
            text=f"Daily Agenda for {self.selected_date.strftime('%A, %B %d')}",
            font=Theme.font_header(),
            text_color=colors["text_primary"]
        ).pack(anchor="w", pady=(0, 10))

        if not events and not tasks:
            empty_box = ctk.CTkFrame(scroll_agenda, fg_color="transparent")
            empty_box.pack(fill="x", pady=30)
            ctk.CTkLabel(
                empty_box,
                text="Nothing scheduled for this day yet.\nClick 'Schedule Event' to plan your agenda.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"],
                justify="center"
            ).pack()
            return

        for ev in events:
            card = ctk.CTkFrame(scroll_agenda, fg_color=colors["bg_card_secondary"], corner_radius=10, border_width=1, border_color=colors["border_subtle"])
            card.pack(fill="x", pady=4)
            c_in = ctk.CTkFrame(card, fg_color="transparent")
            c_in.pack(fill="x", padx=14, pady=10)

            top_row = ctk.CTkFrame(c_in, fg_color="transparent")
            top_row.pack(fill="x")

            badge_txt = ev.get("event_type", "Event")
            badge_bg = colors["accent_pink"] if badge_txt in ("Exam", "Deadline") else colors["accent_blue"]
            ctk.CTkLabel(
                top_row,
                text=f" {badge_txt} ",
                font=Theme.font_tag(),
                fg_color=badge_bg,
                text_color="#FFFFFF",
                corner_radius=4
            ).pack(side="left", padx=(0, 6))

            ctk.CTkLabel(top_row, text=ev["title"], font=Theme.font_body_bold(), text_color=colors["text_primary"], anchor="w").pack(side="left", fill="x", expand=True)

            btn_del = ctk.CTkButton(
                top_row,
                text="",
                image=icons.get_icon("trash", size=13, color="#D94161"),
                width=26,
                height=26,
                fg_color="transparent",
                hover_color=colors["bg_card"],
                command=lambda eid=ev["id"]: self._delete_event(eid)
            )
            btn_del.pack(side="right", padx=(2, 0))

            btn_edit = ctk.CTkButton(
                top_row,
                text="",
                image=icons.get_icon("edit", size=13, color=colors["text_secondary"]),
                width=26,
                height=26,
                fg_color="transparent",
                hover_color=colors["bg_card"],
                command=lambda ed=ev: self._open_edit_event_modal(ed)
            )
            btn_edit.pack(side="right")

            time_str = f"Time: {ev.get('start_time', '')} - {ev.get('end_time', '')}" if ev.get('start_time') else ""
            notes_str = f"Notes: {ev.get('notes')}" if ev.get('notes') else ""
            sub_str = f"Course: {ev.get('subject_name')}" if ev.get('subject_name') else ""
            info_line = "  •  ".join(filter(None, [time_str, sub_str, notes_str]))
            if info_line:
                ctk.CTkLabel(c_in, text=info_line, font=Theme.font_small(), text_color=colors["text_secondary"], anchor="w").pack(anchor="w", pady=(3, 0))

        for t in tasks:
            card = ctk.CTkFrame(scroll_agenda, fg_color=colors["bg_card_secondary"], corner_radius=10, border_width=1, border_color=colors["border_subtle"])
            card.pack(fill="x", pady=4)
            c_in = ctk.CTkFrame(card, fg_color="transparent")
            c_in.pack(fill="x", padx=14, pady=10)

            top_row = ctk.CTkFrame(c_in, fg_color="transparent")
            top_row.pack(fill="x")

            is_done = bool(t["completed"])
            var_chk = tk.BooleanVar(value=is_done)
            chk = ctk.CTkCheckBox(
                top_row,
                text="",
                variable=var_chk,
                width=20,
                checkbox_width=18,
                checkbox_height=18,
                corner_radius=4,
                fg_color=colors["accent_pink"],
                hover_color=colors["accent_pink_hover"],
                border_color=colors["border"],
                command=lambda tid=t["id"], v=var_chk: self._toggle_task(tid, v.get())
            )
            chk.pack(side="left", padx=(0, 6))

            ctk.CTkLabel(
                top_row,
                text=t["title"],
                font=Theme.font_body_bold(),
                text_color=colors["text_muted"] if is_done else colors["text_primary"],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            btn_del = ctk.CTkButton(
                top_row,
                text="",
                image=icons.get_icon("trash", size=13, color="#D94161"),
                width=26,
                height=26,
                fg_color="transparent",
                hover_color=colors["bg_card"],
                command=lambda tid=t["id"]: self._delete_task(tid)
            )
            btn_del.pack(side="right", padx=(2, 0))

            btn_edit = ctk.CTkButton(
                top_row,
                text="",
                image=icons.get_icon("edit", size=13, color=colors["text_secondary"]),
                width=26,
                height=26,
                fg_color="transparent",
                hover_color=colors["bg_card"],
                command=lambda td=t: self._open_edit_task_modal(td)
            )
            btn_edit.pack(side="right")

            meta_str = f"Category: {t.get('category')}  •  Priority: {t.get('priority')}  •  Due: {t.get('due_time', '23:59')}"
            ctk.CTkLabel(c_in, text=meta_str, font=Theme.font_small(), text_color=colors["text_secondary"], anchor="w").pack(anchor="w", pady=(3, 0))

    def _open_add_event_modal(self, default_date: Optional[str] = None):
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
            ToastNotification.show(self.winfo_toplevel(), "Event scheduled.", color_theme="pink")
            self.refresh()

        EventModal(self.winfo_toplevel(), on_saved, default_date=default_date or self.selected_date.isoformat())

    def _open_edit_event_modal(self, event_data: dict):
        def on_saved(data):
            database.update_calendar_event(
                event_id=data["id"],
                title=data["title"],
                event_type=data["event_type"],
                subject_id=data["subject_id"],
                start_date=data["start_date"],
                start_time=data["start_time"],
                end_date=data["end_date"],
                end_time=data["end_time"],
                notes=data["notes"]
            )
            ToastNotification.show(self.winfo_toplevel(), "Event updated.", color_theme="pink")
            self.refresh()

        EventModal(self.winfo_toplevel(), on_saved, event_data=event_data)

    def _delete_event(self, event_id: int):
        database.delete_calendar_event(event_id)
        ToastNotification.show(self.winfo_toplevel(), "Event deleted.", color_theme="pink")
        self.refresh()

    def _open_edit_task_modal(self, task_data: dict):
        def on_saved(data):
            database.update_task(
                task_id=data["id"],
                title=data["title"],
                description=data.get("description", ""),
                subject_id=data.get("subject_id"),
                category=data.get("category", "Study"),
                priority=data.get("priority", "Medium"),
                due_date=data.get("due_date"),
                due_time=data.get("due_time", "23:59")
            )
            ToastNotification.show(self.winfo_toplevel(), "Task updated.", color_theme="mint")
            self.refresh()

        TaskModal(self.winfo_toplevel(), on_saved, task_data=task_data)

    def _delete_task(self, task_id: int):
        database.delete_task(task_id)
        ToastNotification.show(self.winfo_toplevel(), "Task deleted.", color_theme="blue")
        self.refresh()

    def _toggle_task(self, task_id: int, completed: bool):
        database.toggle_task_completed(task_id, completed)
        self.refresh()

"""
ui/calendar_view.py - Modern Cozy Pastel Calendar for Chiikawa Study Planner
Features Month, Week, and Day modes, custom category color coding, interactive legend,
category manager, responsive grid cells with multi-event indicators, and an organized day sidebar.
"""

import tkinter as tk
from tkinter import colorchooser
import customtkinter as ctk
import calendar
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from theme import Theme
import database
import icons
import assets_mgr
from ui.components.widgets import (
    Card,
    PrimaryButton,
    SecondaryButton,
    GhostButton,
    StyledCheckBox
)
from ui.components.modal import (
    EventModal,
    TaskModal,
    CategoryManagerModal
)
from ui.components.toast import ToastNotification


class CalendarView(ctk.CTkFrame):
    """Calendar view with Month, Week, and Day modes, custom color-coding, and day sidebar."""

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

        # Top Control Bar & Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        # Row 1: Period Navigation (Left) & View Switcher / Action (Right)
        nav_row = ctk.CTkFrame(header, fg_color="transparent")
        nav_row.pack(fill="x", pady=(0, 10))

        left_nav = ctk.CTkFrame(nav_row, fg_color="transparent")
        left_nav.pack(side="left")

        ic_prev = icons.get_icon("chevron_left", size=16, color=colors["text_primary"])
        self.btn_prev = ctk.CTkButton(
            left_nav,
            text="",
            image=ic_prev,
            width=38,
            height=38,
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
            width=38,
            height=38,
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
            width=72,
            height=38,
            command=self._go_today
        )
        self.btn_today.pack(side="left", padx=(0, 14))

        self.lbl_period = ctk.CTkLabel(
            left_nav,
            text="",
            font=Theme.font_page_title(),
            text_color=colors["text_primary"]
        )
        self.lbl_period.pack(side="left")

        # Right Controls: View Switcher & Schedule Event
        right_controls = ctk.CTkFrame(nav_row, fg_color="transparent")
        right_controls.pack(side="right")

        self.seg_view = ctk.CTkSegmentedButton(
            right_controls,
            values=["Month", "Week", "Day"],
            font=Theme.font_body(),
            height=38,
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

        ic_plus = icons.get_icon("plus", size=15, color="#FFFFFF")
        btn_add_event = PrimaryButton(
            right_controls,
            text=" Schedule Event",
            image=ic_plus,
            command=self._open_add_event_modal,
            width=150,
            height=38
        )
        btn_add_event.pack(side="left")

        # Row 2: Category Legend & Category Settings Strip
        self.legend_strip = ctk.CTkFrame(header, fg_color="transparent")
        self.legend_strip.pack(fill="x")
        self._render_legend_strip()

        # Main Calendar Container Area
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Build Month Container structure
        self._init_month_view_structure()

    def _render_legend_strip(self):
        colors = Theme.current()
        for child in self.legend_strip.winfo_children():
            child.destroy()

        categories = database.get_event_categories()

        left_legend = ctk.CTkFrame(self.legend_strip, fg_color="transparent")
        left_legend.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_legend,
            text="Legend:",
            font=Theme.font_tag(),
            text_color=colors["text_secondary"]
        ).pack(side="left", padx=(0, 8))

        # Show category pills
        for cat in categories[:7]:
            chip = ctk.CTkFrame(left_legend, fg_color=colors["bg_card"], corner_radius=12, border_width=1, border_color=colors["border_subtle"])
            chip.pack(side="left", padx=3)

            c_inner = ctk.CTkFrame(chip, fg_color="transparent")
            c_inner.pack(padx=8, pady=3)

            # Dot
            ctk.CTkLabel(
                c_inner,
                text="",
                width=8,
                height=8,
                corner_radius=4,
                fg_color=cat["color"]
            ).pack(side="left", padx=(0, 5))

            ctk.CTkLabel(
                c_inner,
                text=cat["name"],
                font=Theme.font_tag(),
                text_color=colors["text_primary"]
            ).pack(side="left")

        # Manage Categories Button
        ic_palette = icons.get_icon("palette", size=13, color=colors["accent_pink"])
        btn_manage_cats = ctk.CTkButton(
            self.legend_strip,
            text=" Categories",
            image=ic_palette,
            compound="left",
            font=Theme.font_tag(),
            fg_color="transparent",
            hover_color=colors["bg_card"],
            text_color=colors["accent_pink"],
            corner_radius=8,
            height=26,
            command=self._open_category_manager
        )
        btn_manage_cats.pack(side="right")

    def _init_month_view_structure(self):
        colors = Theme.current()
        self.month_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.month_container.pack(fill="both", expand=True)
        self.month_container.grid_columnconfigure(0, weight=7)
        self.month_container.grid_columnconfigure(1, weight=3)
        self.month_container.grid_rowconfigure(0, weight=1)

        # Left: Calendar Grid Card
        grid_card = Card(
            self.month_container,
            corner_radius=16,
            hoverable=False
        )
        grid_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Day Headers (Mon - Sun)
        days_header = ctk.CTkFrame(grid_card, fg_color="transparent", height=32)
        days_header.pack(fill="x", padx=12, pady=(12, 6))
        days_header.grid_columnconfigure(tuple(range(7)), weight=1)

        for col_idx, d_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            ctk.CTkLabel(
                days_header,
                text=d_name,
                font=Theme.font_subheader(),
                text_color=colors["accent_pink"] if col_idx in (5, 6) else colors["text_secondary"]
            ).grid(row=0, column=col_idx, sticky="nsew")

        cells_frame = ctk.CTkFrame(grid_card, fg_color="transparent")
        cells_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for r in range(6):
            cells_frame.grid_rowconfigure(r, weight=1)
        cells_frame.grid_columnconfigure(tuple(range(7)), weight=1)

        # Pre-allocate 42 cell frames
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

                # Top row inside cell: day number and tasks badge
                top_row = tk.Frame(cell, bg=colors["bg_card"])
                top_row.pack(fill="x", padx=4, pady=(3, 1))

                lbl_num = tk.Label(
                    top_row,
                    text="",
                    font=Theme.font_small(),
                    fg=colors["text_primary"],
                    bg=colors["bg_card"],
                    padx=4,
                    pady=1
                )
                lbl_num.pack(side="left")

                lbl_task_chip = tk.Label(
                    top_row,
                    text="",
                    font=(Theme.FONT_FAMILY, 8, "bold"),
                    fg=colors["text_primary"],
                    bg=colors["accent_yellow"],
                    padx=3,
                    pady=0
                )

                # Container for event strips
                events_box = tk.Frame(cell, bg=colors["bg_card"])
                events_box.pack(fill="both", expand=True, padx=3, pady=(0, 2))

                # Event strip 1
                ev_strip_1 = tk.Label(
                    events_box,
                    text="",
                    font=(Theme.FONT_FAMILY, 9),
                    anchor="w",
                    padx=4,
                    pady=1
                )

                # Event strip 2
                ev_strip_2 = tk.Label(
                    events_box,
                    text="",
                    font=(Theme.FONT_FAMILY, 9),
                    anchor="w",
                    padx=4,
                    pady=1
                )

                # More indicator label (+N more)
                lbl_more = tk.Label(
                    events_box,
                    text="",
                    font=(Theme.FONT_FAMILY, 8, "bold"),
                    fg=colors["accent_pink"],
                    bg=colors["bg_card"],
                    anchor="w",
                    padx=4,
                    pady=0
                )

                cell_data = {
                    "cell": cell,
                    "top_row": top_row,
                    "lbl_num": lbl_num,
                    "lbl_task_chip": lbl_task_chip,
                    "events_box": events_box,
                    "ev_strip_1": ev_strip_1,
                    "ev_strip_2": ev_strip_2,
                    "lbl_more": lbl_more,
                    "day_obj": None,
                    "events": []
                }

                def make_click_handler(cd):
                    return lambda e: self._select_day(cd["day_obj"])

                def make_dbl_click_handler(cd):
                    return lambda e: self._open_add_event_modal(default_date=cd["day_obj"].isoformat() if cd["day_obj"] else None)

                for w in [cell, top_row, lbl_num, lbl_task_chip, events_box, ev_strip_1, ev_strip_2, lbl_more]:
                    w.bind("<Button-1>", make_click_handler(cell_data))
                    w.bind("<Double-Button-1>", make_dbl_click_handler(cell_data))

                self.grid_cells.append(cell_data)

        # Right: Day Inspector Panel
        self.inspector_card = Card(
            self.month_container,
            corner_radius=16,
            hoverable=False
        )
        self.inspector_card.grid(row=0, column=1, sticky="nsew")

        # Day Inspector Top Header
        ins_header = ctk.CTkFrame(self.inspector_card, fg_color="transparent")
        ins_header.pack(fill="x", padx=16, pady=(16, 10))

        title_line = ctk.CTkFrame(ins_header, fg_color="transparent")
        title_line.pack(fill="x", pady=(0, 4))

        self.lbl_ins_date = ctk.CTkLabel(
            title_line,
            text="",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        )
        self.lbl_ins_date.pack(side="left")

        self.lbl_ins_tag = ctk.CTkLabel(
            title_line,
            text="",
            font=Theme.font_tag(),
            fg_color=colors["accent_pink_subtle"],
            text_color=colors["accent_pink"],
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.lbl_ins_tag.pack(side="right")

        # Action Buttons row: Add Event and Add Task
        ins_actions = ctk.CTkFrame(ins_header, fg_color="transparent")
        ins_actions.pack(fill="x", pady=(6, 0))
        ins_actions.grid_columnconfigure((0, 1), weight=1)

        btn_add_ev = ctk.CTkButton(
            ins_actions,
            text="+ Event",
            font=Theme.font_body_bold(),
            fg_color=colors["accent_pink"],
            hover_color=colors["accent_pink_hover"],
            text_color="#FFFFFF",
            corner_radius=8,
            height=32,
            command=lambda: self._open_add_event_modal(default_date=self.selected_date.isoformat())
        )
        btn_add_ev.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        btn_add_tk = ctk.CTkButton(
            ins_actions,
            text="+ Task",
            font=Theme.font_body_bold(),
            fg_color=colors["bg_card_secondary"],
            hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            border_width=1,
            border_color=colors["border"],
            corner_radius=8,
            height=32,
            command=self._open_add_task_modal
        )
        btn_add_tk.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Agenda Filter Toggle: All / Events / Tasks
        self.inspector_filter = "All"
        self.seg_filter = ctk.CTkSegmentedButton(
            ins_header,
            values=["All", "Events", "Tasks"],
            font=Theme.font_tag(),
            height=28,
            corner_radius=8,
            selected_color=colors["accent_pink"],
            selected_hover_color=colors["accent_pink_hover"],
            unselected_color=colors["bg_card"],
            unselected_hover_color=colors["bg_sidebar_hover"],
            text_color=colors["text_primary"],
            command=self._on_filter_changed
        )
        self.seg_filter.set("All")
        self.seg_filter.pack(fill="x", pady=(8, 0))

        # Day Inspector Scrollable List
        self.ins_scroll = ctk.CTkScrollableFrame(
            self.inspector_card,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.ins_scroll.pack(fill="both", expand=True, padx=14, pady=(6, 14))

    def _on_filter_changed(self, mode: str):
        self.inspector_filter = mode
        self._update_inspector()

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
        self._render_legend_strip()
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
    # Month View Implementation
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

            # Styling colors
            if is_selected:
                cell_bg = colors["bg_sidebar_active"]
                border_col = colors["accent_pink"]
                border_w = 2
            else:
                cell_bg = colors["bg_card"] if is_cur_month else colors["bg_card_secondary"]
                border_col = colors["border_subtle"]
                border_w = 1

            cell_data["cell"].configure(bg=cell_bg, highlightbackground=border_col, highlightthickness=border_w)
            cell_data["top_row"].configure(bg=cell_bg)
            cell_data["events_box"].configure(bg=cell_bg)

            # Day Number badge
            if is_today:
                cell_data["lbl_num"].configure(
                    text=str(day_obj.day),
                    fg="#FFFFFF",
                    bg=colors["accent_pink"],
                    font=(Theme.FONT_FAMILY, 9, "bold")
                )
            else:
                num_fg = colors["text_primary"] if is_cur_month else colors["text_muted"]
                cell_data["lbl_num"].configure(
                    text=str(day_obj.day),
                    fg=num_fg,
                    bg=cell_bg,
                    font=Theme.font_small()
                )

            day_events = events_by_date.get(d_str, [])
            cell_data["events"] = day_events
            day_tasks = tasks_by_date.get(d_str, [])

            # Task chip in top row
            uncompleted = sum(1 for t in day_tasks if not t["completed"])
            if uncompleted > 0:
                is_overdue = (day_obj < today_obj and uncompleted > 0)
                chip_bg = colors["priority_high_bg"] if is_overdue else colors["accent_yellow"]
                chip_fg = colors["priority_high_fg"] if is_overdue else colors["text_primary"]
                cell_data["lbl_task_chip"].configure(
                    text=f"✓{uncompleted}",
                    bg=chip_bg,
                    fg=chip_fg
                )
                cell_data["lbl_task_chip"].pack(side="right")
            else:
                cell_data["lbl_task_chip"].pack_forget()

            # Event strip 1
            if len(day_events) >= 1:
                ev1 = day_events[0]
                col1 = ev1.get("color") or database.get_category_color(ev1.get("category", "Event"))
                txt_col1 = database.get_contrast_text_color(col1)
                cell_data["ev_strip_1"].configure(
                    text=ev1["title"],
                    bg=col1,
                    fg=txt_col1
                )
                cell_data["ev_strip_1"].pack(fill="x", pady=1)
            else:
                cell_data["ev_strip_1"].pack_forget()

            # Event strip 2
            if len(day_events) >= 2:
                ev2 = day_events[1]
                col2 = ev2.get("color") or database.get_category_color(ev2.get("category", "Event"))
                txt_col2 = database.get_contrast_text_color(col2)
                cell_data["ev_strip_2"].configure(
                    text=ev2["title"],
                    bg=col2,
                    fg=txt_col2
                )
                cell_data["ev_strip_2"].pack(fill="x", pady=1)
            else:
                cell_data["ev_strip_2"].pack_forget()

            # More indicator (+N more)
            if len(day_events) > 2:
                more_count = len(day_events) - 2
                cell_data["lbl_more"].configure(
                    text=f"+{more_count} more",
                    bg=cell_bg,
                    fg=colors["accent_pink"]
                )
                cell_data["lbl_more"].pack(anchor="w", pady=(1, 0))
            else:
                cell_data["lbl_more"].pack_forget()

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

        # Instant cell highlight update
        colors = Theme.current()
        today_obj = date.today()
        for cell_data in self.grid_cells:
            cd = cell_data["day_obj"]
            if cd in (old_date, day_obj):
                is_cur_month = (cd.month == self.selected_date.month)
                is_selected = (cd == self.selected_date)
                is_today = (cd == today_obj)

                if is_selected:
                    cell_bg = colors["bg_sidebar_active"]
                    border_col = colors["accent_pink"]
                    border_w = 2
                else:
                    cell_bg = colors["bg_card"] if is_cur_month else colors["bg_card_secondary"]
                    border_col = colors["border_subtle"]
                    border_w = 1

                cell_data["cell"].configure(bg=cell_bg, highlightbackground=border_col, highlightthickness=border_w)
                cell_data["top_row"].configure(bg=cell_bg)
                cell_data["events_box"].configure(bg=cell_bg)

                if is_today:
                    cell_data["lbl_num"].configure(
                        text=str(cd.day),
                        fg="#FFFFFF",
                        bg=colors["accent_pink"],
                        font=(Theme.FONT_FAMILY, 9, "bold")
                    )
                else:
                    num_fg = colors["text_primary"] if is_cur_month else colors["text_muted"]
                    cell_data["lbl_num"].configure(
                        text=str(cd.day),
                        fg=num_fg,
                        bg=cell_bg,
                        font=Theme.font_small()
                    )

                if len(cell_data["events"]) > 2:
                    cell_data["lbl_more"].configure(bg=cell_bg)

        self._update_inspector()

    def _update_inspector(self):
        colors = Theme.current()
        today_obj = date.today()

        # Date heading & relative tag
        self.lbl_ins_date.configure(text=self.selected_date.strftime("%A, %B %d, %Y"))
        
        diff = (self.selected_date - today_obj).days
        if diff == 0:
            rel_text = "Today"
            tag_bg = colors["accent_pink_subtle"]
            tag_fg = colors["accent_pink"]
        elif diff == 1:
            rel_text = "Tomorrow"
            tag_bg = colors["priority_med_bg"]
            tag_fg = colors["priority_med_fg"]
        elif diff == -1:
            rel_text = "Yesterday"
            tag_bg = colors["bg_card_secondary"]
            tag_fg = colors["text_muted"]
        elif diff > 0:
            rel_text = f"In {diff} days"
            tag_bg = colors["bg_card_secondary"]
            tag_fg = colors["text_secondary"]
        else:
            rel_text = f"{abs(diff)} days ago"
            tag_bg = colors["bg_card_secondary"]
            tag_fg = colors["text_muted"]

        self.lbl_ins_tag.configure(text=rel_text, fg_color=tag_bg, text_color=tag_fg)

        for child in self.ins_scroll.winfo_children():
            child.destroy()

        sel_str = self.selected_date.isoformat()
        events = database.get_calendar_events(sel_str, sel_str)
        tasks = database.get_tasks(due_date=sel_str)

        filter_mode = getattr(self, "inspector_filter", "All")
        display_events = sorted(events, key=lambda x: x.get("start_time") or "00:00") if filter_mode in ("All", "Events") else []
        display_tasks = sorted(tasks, key=lambda x: x.get("due_time") or "23:59") if filter_mode in ("All", "Tasks") else []

        # Empty state when nothing scheduled
        if not display_events and not display_tasks:
            empty_box = ctk.CTkFrame(self.ins_scroll, fg_color="transparent")
            empty_box.pack(fill="both", expand=True, pady=25)

            mascot = assets_mgr.get_illustration("study", size=(90, 90))
            if mascot:
                ctk.CTkLabel(empty_box, image=mascot, text="").pack(pady=(0, 10))

            if filter_mode == "Events":
                empty_msg = "No events scheduled for this day"
                btn_txt = "+ Schedule Event"
                btn_cmd = lambda: self._open_add_event_modal(default_date=self.selected_date.isoformat())
            elif filter_mode == "Tasks":
                empty_msg = "No tasks due on this day"
                btn_txt = "+ Add Task"
                btn_cmd = self._open_add_task_modal
            else:
                empty_msg = "No items scheduled for this day"
                btn_txt = "+ Schedule Event"
                btn_cmd = lambda: self._open_add_event_modal(default_date=self.selected_date.isoformat())

            ctk.CTkLabel(
                empty_box,
                text=empty_msg,
                font=Theme.font_card_title(),
                text_color=colors["text_primary"]
            ).pack(pady=(0, 4))

            ctk.CTkLabel(
                empty_box,
                text="Relax with Chiikawa or plan your study session ahead!",
                font=Theme.font_small(),
                text_color=colors["text_secondary"],
                justify="center"
            ).pack(pady=(0, 16))

            btn_empty_add = PrimaryButton(
                empty_box,
                text=btn_txt,
                width=150,
                height=34,
                command=btn_cmd
            )
            btn_empty_add.pack()
            return

        # 1. Events Section
        if display_events:
            h_row = ctk.CTkFrame(self.ins_scroll, fg_color="transparent")
            h_row.pack(fill="x", pady=(2, 6))

            ctk.CTkLabel(
                h_row,
                text="Events & Schedule",
                font=Theme.font_subheader(),
                text_color=colors["text_primary"]
            ).pack(side="left")

            ctk.CTkLabel(
                h_row,
                text=f"{len(display_events)}",
                font=Theme.font_tag(),
                fg_color=colors["bg_card_secondary"],
                text_color=colors["text_secondary"],
                corner_radius=6,
                padx=6,
                pady=1
            ).pack(side="left", padx=(6, 0))

            for ev in display_events:
                ev_card = Card(
                    self.ins_scroll,
                    corner_radius=10,
                    fg_color=colors["bg_card"],
                    hoverable=True
                )
                ev_card.pack(fill="x", pady=4)

                ev_inner = ctk.CTkFrame(ev_card, fg_color="transparent")
                ev_inner.pack(fill="x", padx=10, pady=8)

                # Top row: Category color pill, title, and action buttons
                top_row = ctk.CTkFrame(ev_inner, fg_color="transparent")
                top_row.pack(fill="x")

                cat_name = ev.get("category") or ev.get("event_type") or "Event"
                cat_col = ev.get("color") or database.get_category_color(cat_name)
                txt_col = database.get_contrast_text_color(cat_col)

                ctk.CTkLabel(
                    top_row,
                    text=f" {cat_name} ",
                    font=Theme.font_tag(),
                    fg_color=cat_col,
                    text_color=txt_col,
                    corner_radius=4,
                    padx=4,
                    pady=1
                ).pack(side="left", padx=(0, 8))

                ctk.CTkLabel(
                    top_row,
                    text=ev["title"],
                    font=Theme.font_body_bold(),
                    text_color=colors["text_primary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)

                # Action buttons: Delete, Edit, Duplicate
                btn_del = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("trash", size=13, color="#D94161"),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card_secondary"],
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
                    hover_color=colors["bg_card_secondary"],
                    command=lambda ed=ev: self._open_edit_event_modal(ed)
                )
                btn_edit.pack(side="right", padx=(2, 0))

                btn_dup = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("copy", size=13, color=colors["text_secondary"]),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card_secondary"],
                    command=lambda eid=ev["id"]: self._duplicate_event(eid)
                )
                btn_dup.pack(side="right")

                # Details row
                meta_parts = []
                if ev.get("start_time"):
                    end_t = ev.get("end_time")
                    meta_parts.append(f"⏰ {ev['start_time']} - {end_t}" if end_t else f"⏰ {ev['start_time']}")
                if ev.get("location"):
                    meta_parts.append(f"📍 {ev['location']}")
                if ev.get("subject_name"):
                    meta_parts.append(f"📚 {ev['subject_name']}")
                if ev.get("reminder") and ev.get("reminder") != "None":
                    meta_parts.append(f"🔔 {ev['reminder']}")
                if ev.get("recurring") and ev.get("recurring") != "None":
                    meta_parts.append(f"🔁 {ev['recurring']}")
                if ev.get("notes"):
                    meta_parts.append(f"📝 {ev['notes']}")

                if meta_parts:
                    ctk.CTkLabel(
                        ev_inner,
                        text="  •  ".join(meta_parts),
                        font=Theme.font_small(),
                        text_color=colors["text_secondary"],
                        anchor="w"
                    ).pack(anchor="w", pady=(4, 0))

                # Click on card opens edit modal
                ev_card.bind("<Button-1>", lambda e, ed=ev: self._open_edit_event_modal(ed))
                ev_inner.bind("<Button-1>", lambda e, ed=ev: self._open_edit_event_modal(ed))

        # 2. Tasks Due Section
        if display_tasks:
            t_row = ctk.CTkFrame(self.ins_scroll, fg_color="transparent")
            t_row.pack(fill="x", pady=(12, 6))

            ctk.CTkLabel(
                t_row,
                text="Tasks Due Today",
                font=Theme.font_subheader(),
                text_color=colors["text_primary"]
            ).pack(side="left")

            ctk.CTkLabel(
                t_row,
                text=f"{len(display_tasks)}",
                font=Theme.font_tag(),
                fg_color=colors["bg_card_secondary"],
                text_color=colors["text_secondary"],
                corner_radius=6,
                padx=6,
                pady=1
            ).pack(side="left", padx=(6, 0))

            for t in display_tasks:
                t_card = Card(
                    self.ins_scroll,
                    corner_radius=10,
                    fg_color=colors["bg_card"],
                    hoverable=True
                )
                t_card.pack(fill="x", pady=4)

                t_inner = ctk.CTkFrame(t_card, fg_color="transparent")
                t_inner.pack(fill="x", padx=10, pady=8)

                top_row = ctk.CTkFrame(t_inner, fg_color="transparent")
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
                chk.pack(side="left", padx=(0, 8))

                title_color = colors["text_muted"] if is_done else colors["text_primary"]
                ctk.CTkLabel(
                    top_row,
                    text=t["title"],
                    font=Theme.font_body_bold(),
                    text_color=title_color,
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)

                # Priority Badge
                prio = t.get("priority", "Medium")
                if prio == "High":
                    prio_bg, prio_fg = colors["priority_high_bg"], colors["priority_high_fg"]
                elif prio == "Medium":
                    prio_bg, prio_fg = colors["priority_med_bg"], colors["priority_med_fg"]
                else:
                    prio_bg, prio_fg = colors["priority_low_bg"], colors["priority_low_fg"]

                ctk.CTkLabel(
                    top_row,
                    text=f" {prio} ",
                    font=Theme.font_tag(),
                    fg_color=prio_bg,
                    text_color=prio_fg,
                    corner_radius=4,
                    padx=4,
                    pady=1
                ).pack(side="right", padx=(6, 0))

                # Delete & Edit buttons
                btn_del = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("trash", size=13, color="#D94161"),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card_secondary"],
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
                    hover_color=colors["bg_card_secondary"],
                    command=lambda td=t: self._open_edit_task_modal(td)
                )
                btn_edit.pack(side="right")

                # Meta line
                meta_parts = []
                if t.get("category"):
                    meta_parts.append(f"Category: {t['category']}")
                if t.get("due_time"):
                    meta_parts.append(f"Due: {t['due_time']}")
                if self.selected_date < today_obj and not is_done:
                    meta_parts.append("⚠️ Overdue")

                if meta_parts:
                    ctk.CTkLabel(
                        t_inner,
                        text="  •  ".join(meta_parts),
                        font=Theme.font_small(),
                        text_color=colors["priority_high_fg"] if (self.selected_date < today_obj and not is_done) else colors["text_secondary"],
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
            self.week_container = Card(
                self.main_content,
                corner_radius=16,
                hoverable=False
            )
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
            is_selected = (cur_d == self.selected_date)

            col_bg = colors["bg_sidebar_active"] if is_selected else (colors["bg_card"] if is_today else colors["bg_card_secondary"])
            border_col = colors["accent_pink"] if (is_selected or is_today) else colors["border_subtle"]

            col_card = Card(
                self.week_container,
                corner_radius=12,
                fg_color=col_bg,
                border_color=border_col,
                hoverable=False
            )
            col_card.grid(row=0, column=i, sticky="nsew", padx=3, pady=10)

            # Column Header
            h_frame = ctk.CTkFrame(col_card, fg_color="transparent")
            h_frame.pack(fill="x", padx=6, pady=(10, 6))

            ctk.CTkLabel(
                h_frame,
                text=cur_d.strftime("%a"),
                font=Theme.font_subheader(),
                text_color=colors["accent_pink"] if cur_d.weekday() in (5, 6) else colors["text_secondary"]
            ).pack()

            if is_today:
                date_pill = ctk.CTkLabel(
                    h_frame,
                    text=str(cur_d.day),
                    font=Theme.font_card_title(),
                    fg_color=colors["accent_pink"],
                    text_color="#FFFFFF",
                    corner_radius=12,
                    width=32,
                    height=32
                )
                date_pill.pack(pady=(2, 0))
            else:
                ctk.CTkLabel(
                    h_frame,
                    text=str(cur_d.day),
                    font=Theme.font_card_title(),
                    text_color=colors["text_primary"]
                ).pack()

            # Column Items Scroll
            scroll_day = ctk.CTkScrollableFrame(
                col_card,
                fg_color="transparent",
                scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
                scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
            )
            scroll_day.pack(fill="both", expand=True, padx=4, pady=(4, 8))

            day_events = [ev for ev in events if ev["start_date"] == cur_str]
            for ev in day_events:
                cat_col = ev.get("color") or database.get_category_color(ev.get("category", "Event"))
                txt_col = database.get_contrast_text_color(cat_col)

                ev_pill = ctk.CTkFrame(scroll_day, fg_color=cat_col, corner_radius=6)
                ev_pill.pack(fill="x", pady=2)

                ctk.CTkLabel(
                    ev_pill,
                    text=ev["title"],
                    font=Theme.font_tag(),
                    text_color=txt_col,
                    wraplength=105
                ).pack(padx=6, pady=4)

                ev_pill.bind("<Button-1>", lambda e, ed=ev: self._open_edit_event_modal(ed))

            day_tasks = [t for t in tasks if t.get("due_date") == cur_str]
            for t in day_tasks:
                is_done = bool(t["completed"])
                t_pill = ctk.CTkFrame(scroll_day, fg_color=colors["bg_card"], corner_radius=6, border_width=1, border_color=colors["border_subtle"])
                t_pill.pack(fill="x", pady=2)

                ctk.CTkLabel(
                    t_pill,
                    text=f"✓ {t['title']}" if is_done else t['title'],
                    font=Theme.font_tag(),
                    text_color=colors["text_muted"] if is_done else colors["text_primary"],
                    wraplength=105
                ).pack(padx=6, pady=4)

                t_pill.bind("<Button-1>", lambda e, td=t: self._open_edit_task_modal(td))

            # Click column selects date
            col_card.bind("<Button-1>", lambda e, d=cur_d: self._select_day(d))
            col_card.bind("<Double-Button-1>", lambda e, d=cur_d: self._open_add_event_modal(default_date=d.isoformat()))

    # -------------------------------------------------------------
    # Day View Implementation
    # -------------------------------------------------------------
    def _render_day_view(self):
        colors = Theme.current()
        self.lbl_period.configure(text=self.selected_date.strftime("%A, %B %d, %Y"))

        if not self.day_container:
            self.day_container = Card(
                self.main_content,
                corner_radius=16,
                hoverable=False
            )
        self.day_container.pack(fill="both", expand=True)

        for child in self.day_container.winfo_children():
            child.destroy()

        scroll_agenda = ctk.CTkScrollableFrame(
            self.day_container,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        scroll_agenda.pack(fill="both", expand=True, padx=24, pady=16)

        sel_str = self.selected_date.isoformat()
        events = database.get_calendar_events(sel_str, sel_str)
        tasks = database.get_tasks(due_date=sel_str)

        # Header title
        ctk.CTkLabel(
            scroll_agenda,
            text=f"Daily Agenda for {self.selected_date.strftime('%A, %B %d')}",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w", pady=(0, 12))

        if not events and not tasks:
            empty_box = ctk.CTkFrame(scroll_agenda, fg_color="transparent")
            empty_box.pack(fill="both", expand=True, pady=40)

            mascot = assets_mgr.get_illustration("coffee", size=(100, 100))
            if mascot:
                ctk.CTkLabel(empty_box, image=mascot, text="").pack(pady=(0, 12))

            ctk.CTkLabel(
                empty_box,
                text="Nothing scheduled for this day yet.",
                font=Theme.font_card_title(),
                text_color=colors["text_primary"]
            ).pack(pady=(0, 4))

            ctk.CTkLabel(
                empty_box,
                text="Click 'Schedule Event' or 'Add Task' to plan your agenda.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"],
                justify="center"
            ).pack(pady=(0, 16))

            btn_sched = PrimaryButton(
                empty_box,
                text="+ Schedule Event",
                width=160,
                command=lambda: self._open_add_event_modal(default_date=self.selected_date.isoformat())
            )
            btn_sched.pack()
            return

        # Events list in Day View
        if events:
            ctk.CTkLabel(scroll_agenda, text="Scheduled Events", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(4, 6))

            for ev in events:
                card = Card(scroll_agenda, corner_radius=10, fg_color=colors["bg_card"], hoverable=True)
                card.pack(fill="x", pady=4)

                c_in = ctk.CTkFrame(card, fg_color="transparent")
                c_in.pack(fill="x", padx=14, pady=10)

                top_row = ctk.CTkFrame(c_in, fg_color="transparent")
                top_row.pack(fill="x")

                cat_name = ev.get("category") or ev.get("event_type") or "Event"
                cat_col = ev.get("color") or database.get_category_color(cat_name)
                txt_col = database.get_contrast_text_color(cat_col)

                ctk.CTkLabel(
                    top_row,
                    text=f" {cat_name} ",
                    font=Theme.font_tag(),
                    fg_color=cat_col,
                    text_color=txt_col,
                    corner_radius=4,
                    padx=6,
                    pady=2
                ).pack(side="left", padx=(0, 8))

                ctk.CTkLabel(
                    top_row,
                    text=ev["title"],
                    font=Theme.font_body_bold(),
                    text_color=colors["text_primary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)

                btn_del = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("trash", size=13, color="#D94161"),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card_secondary"],
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
                    hover_color=colors["bg_card_secondary"],
                    command=lambda ed=ev: self._open_edit_event_modal(ed)
                )
                btn_edit.pack(side="right", padx=(2, 0))

                btn_dup = ctk.CTkButton(
                    top_row,
                    text="",
                    image=icons.get_icon("copy", size=13, color=colors["text_secondary"]),
                    width=26,
                    height=26,
                    fg_color="transparent",
                    hover_color=colors["bg_card_secondary"],
                    command=lambda eid=ev["id"]: self._duplicate_event(eid)
                )
                btn_dup.pack(side="right")

                meta_parts = []
                if ev.get("start_time"):
                    end_t = ev.get("end_time")
                    meta_parts.append(f"⏰ {ev['start_time']} - {end_t}" if end_t else f"⏰ {ev['start_time']}")
                if ev.get("location"):
                    meta_parts.append(f"📍 {ev['location']}")
                if ev.get("subject_name"):
                    meta_parts.append(f"📚 {ev['subject_name']}")
                if ev.get("reminder") and ev.get("reminder") != "None":
                    meta_parts.append(f"🔔 {ev['reminder']}")
                if ev.get("recurring") and ev.get("recurring") != "None":
                    meta_parts.append(f"🔁 {ev['recurring']}")
                if ev.get("notes"):
                    meta_parts.append(f"📝 {ev['notes']}")

                if meta_parts:
                    ctk.CTkLabel(
                        c_in,
                        text="  •  ".join(meta_parts),
                        font=Theme.font_small(),
                        text_color=colors["text_secondary"],
                        anchor="w"
                    ).pack(anchor="w", pady=(4, 0))

                card.bind("<Button-1>", lambda e, ed=ev: self._open_edit_event_modal(ed))

        # Tasks list in Day View
        if tasks:
            ctk.CTkLabel(scroll_agenda, text="Tasks Due Today", font=Theme.font_subheader(), text_color=colors["text_primary"]).pack(anchor="w", pady=(14, 6))

            for t in tasks:
                card = Card(scroll_agenda, corner_radius=10, fg_color=colors["bg_card"], hoverable=True)
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
                chk.pack(side="left", padx=(0, 8))

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
                    hover_color=colors["bg_card_secondary"],
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
                    hover_color=colors["bg_card_secondary"],
                    command=lambda td=t: self._open_edit_task_modal(td)
                )
                btn_edit.pack(side="right")

                meta_str = f"Priority: {t.get('priority', 'Medium')}  •  Category: {t.get('category', 'Study')}  •  Due: {t.get('due_time', '23:59')}"
                ctk.CTkLabel(c_in, text=meta_str, font=Theme.font_small(), text_color=colors["text_secondary"], anchor="w").pack(anchor="w", pady=(3, 0))

    # -------------------------------------------------------------
    # Event & Task Modal Handlers
    # -------------------------------------------------------------
    def _open_add_event_modal(self, default_date: Optional[str] = None):
        def on_saved(data):
            database.add_calendar_event(
                title=data["title"],
                event_type=data.get("category") or data.get("event_type", "Event"),
                subject_id=data.get("subject_id"),
                start_date=data["start_date"],
                start_time=data.get("start_time", "09:00"),
                end_date=data.get("end_date") or data["start_date"],
                end_time=data.get("end_time", "10:00"),
                notes=data.get("notes", ""),
                color=data.get("color"),
                location=data.get("location", ""),
                category=data.get("category"),
                reminder=data.get("reminder", "None"),
                recurring=data.get("recurring", "None")
            )
            ToastNotification.show(self.winfo_toplevel(), "Event scheduled.", color_theme="pink")
            self.refresh()

        EventModal(
            self.winfo_toplevel(),
            on_saved,
            default_date=default_date or self.selected_date.isoformat()
        )

    def _open_edit_event_modal(self, event_data: dict):
        def on_saved(data):
            database.update_calendar_event(
                event_id=data["id"],
                title=data["title"],
                event_type=data.get("category") or data.get("event_type", "Event"),
                subject_id=data.get("subject_id"),
                start_date=data["start_date"],
                start_time=data.get("start_time", "09:00"),
                end_date=data.get("end_date") or data["start_date"],
                end_time=data.get("end_time", "10:00"),
                notes=data.get("notes", ""),
                color=data.get("color"),
                location=data.get("location", ""),
                category=data.get("category"),
                reminder=data.get("reminder", "None"),
                recurring=data.get("recurring", "None")
            )
            ToastNotification.show(self.winfo_toplevel(), "Event updated.", color_theme="pink")
            self.refresh()

        def on_duplicate(event_id: int):
            ToastNotification.show(self.winfo_toplevel(), "Event duplicated.", color_theme="mint")
            self.refresh()

        def on_delete(event_id: int):
            self._delete_event(event_id)

        EventModal(
            self.winfo_toplevel(),
            on_saved,
            event_data=event_data,
            on_duplicate=on_duplicate,
            on_delete=on_delete
        )

    def _duplicate_event(self, event_id: int):
        new_id = database.duplicate_calendar_event(event_id)
        if new_id:
            ToastNotification.show(self.winfo_toplevel(), "Event duplicated.", color_theme="mint")
            self.refresh()

    def _delete_event(self, event_id: int):
        database.delete_calendar_event(event_id)
        ToastNotification.show(self.winfo_toplevel(), "Event deleted.", color_theme="pink")
        self.refresh()

    def _open_add_task_modal(self):
        def on_saved(data):
            database.add_task(
                title=data["title"],
                description=data.get("description", ""),
                subject_id=data.get("subject_id"),
                category=data.get("category", "Study"),
                priority=data.get("priority", "Medium"),
                due_date=data.get("due_date") or self.selected_date.isoformat(),
                due_time=data.get("due_time", "23:59")
            )
            ToastNotification.show(self.winfo_toplevel(), "Task added.", color_theme="mint")
            self.refresh()

        TaskModal(
            self.winfo_toplevel(),
            on_saved,
            task_data={"due_date": self.selected_date.isoformat()}
        )

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

    def _open_category_manager(self):
        def on_changed():
            self.refresh()

        CategoryManagerModal(self.winfo_toplevel(), on_changed=on_changed)

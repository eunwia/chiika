"""
ui/progress_view.py - Modern Progress & Statistics View for Chiikawa Study Planner
Displays task completion rates, study hours, focus sessions, weekly study bar chart, and course distribution.
Refactored with PageHeader, Card, StatCard, and modern typography.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Any
from theme import Theme
import database
import assets_mgr
from ui.components.widgets import PageHeader, Card, StatCard


class ProgressView(ctk.CTkFrame):
    """Analytics & progress reporting view with weekly charts and subject distributions."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        # 1. Page Header
        header = PageHeader(
            self,
            title="Analytics & Progress",
            subtitle="Review your study consistency, focus sprint volume, and course allocations."
        )
        header.pack(fill="x", padx=24, pady=(20, 14))

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=(Theme.LIGHT["border_subtle"], Theme.DARK["border_subtle"]),
            scrollbar_button_hover_color=(Theme.LIGHT["accent_pink"], Theme.DARK["accent_pink"])
        )
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def refresh(self):
        colors = Theme.current()
        for child in self.scroll.winfo_children():
            child.destroy()

        stats = database.get_dashboard_stats()
        weekly = database.get_weekly_study_stats()
        subject_dist = database.get_subject_time_distribution()

        # 1. Top Stat Cards (4 metrics)
        stat_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stat_row.pack(fill="x", pady=(0, 18))
        stat_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        total_study_mins = stats["study_minutes_total"]
        tot_hrs = total_study_mins // 60
        tot_mins = total_study_mins % 60
        study_time_str = f"{tot_hrs}h {tot_mins}m" if tot_hrs > 0 else f"{tot_mins}m"

        all_tasks = database.get_tasks()
        tot_tasks = len(all_tasks)
        comp_tasks = sum(1 for t in all_tasks if t["completed"])
        rate_val = int((comp_tasks / tot_tasks * 100)) if tot_tasks > 0 else 0

        pomo_sessions = len(database.get_study_sessions(limit=500))

        card_rate = StatCard(
            stat_row,
            title="Task Completion Rate",
            value=f"{rate_val}%",
            accent_color=colors["accent_pink"],
            icon_name="tasks",
            progress=rate_val / 100.0
        )
        card_rate.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        card_study = StatCard(
            stat_row,
            title="Total Study Time",
            value=study_time_str,
            accent_color=colors["accent_blue"],
            icon_name="timer",
            progress=min(1.0, total_study_mins / 600.0)
        )
        card_study.grid(row=0, column=1, sticky="nsew", padx=6)

        card_pomo = StatCard(
            stat_row,
            title="Sessions Logged",
            value=f"{pomo_sessions}",
            accent_color=colors["accent_yellow"],
            icon_name="study",
            progress=min(1.0, pomo_sessions / 20.0)
        )
        card_pomo.grid(row=0, column=2, sticky="nsew", padx=6)

        card_consistency = StatCard(
            stat_row,
            title="Consistency Status",
            value="Consistent",
            accent_color=colors["accent_mint"],
            icon_name="habits",
            progress=0.9
        )
        card_consistency.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        # 2. Middle Row: Weekly Study Activity Chart & Mascot Banner
        mid_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        mid_row.pack(fill="x", pady=(0, 18))
        mid_row.grid_columnconfigure(0, weight=7)
        mid_row.grid_columnconfigure(1, weight=3)

        chart_card = Card(
            mid_row,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ch_header = ctk.CTkFrame(chart_card, fg_color="transparent")
        ch_header.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(Theme.CARD_PAD_Y, 8))
        ctk.CTkLabel(
            ch_header,
            text="7-Day Study Activity (Minutes)",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        self._render_bar_chart(chart_card, weekly)

        mascot_card = Card(
            mid_row,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        mascot_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        m_inner = ctk.CTkFrame(mascot_card, fg_color="transparent")
        m_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=Theme.CARD_PAD_Y)

        grad_img = assets_mgr.get_illustration("graduate", size=(105, 105))
        if grad_img:
            ctk.CTkLabel(m_inner, image=grad_img, text="").pack(pady=(0, 8))

        ctk.CTkLabel(
            m_inner,
            text="Milestone Achievement",
            font=Theme.font_card_title(),
            text_color=colors["accent_pink"]
        ).pack()

        ctk.CTkLabel(
            m_inner,
            text="'Every minute of focused study brings you closer to mastery!'",
            font=Theme.font_body(),
            text_color=colors["text_secondary"],
            wraplength=190,
            justify="center"
        ).pack(pady=(6, 0))

        # 3. Subject Time Distribution Card
        dist_card = Card(
            self.scroll,
            corner_radius=Theme.RADIUS_LG,
            hoverable=False
        )
        dist_card.pack(fill="x")

        d_header = ctk.CTkFrame(dist_card, fg_color="transparent")
        d_header.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(Theme.CARD_PAD_Y, 10))
        ctk.CTkLabel(
            d_header,
            text="Study Time Distribution by Course",
            font=Theme.font_card_title(),
            text_color=colors["text_primary"]
        ).pack(side="left")

        d_inner = ctk.CTkFrame(dist_card, fg_color="transparent")
        d_inner.pack(fill="both", expand=True, padx=Theme.CARD_PAD_X, pady=(0, Theme.CARD_PAD_Y))

        if not subject_dist:
            ctk.CTkLabel(
                d_inner,
                text="No study sessions recorded yet.",
                font=Theme.font_body(),
                text_color=colors["text_secondary"]
            ).pack(anchor="w", pady=8)
        else:
            max_mins = max(s["total_minutes"] for s in subject_dist) or 1
            for sub_info in subject_dist:
                s_name = sub_info["subject_name"]
                s_mins = sub_info["total_minutes"]
                s_col = sub_info["subject_color"]
                s_hrs = s_mins // 60
                s_rm = s_mins % 60
                display_time = f"{s_hrs}h {s_rm}m" if s_hrs > 0 else f"{s_mins}m"

                row = ctk.CTkFrame(d_inner, fg_color="transparent")
                row.pack(fill="x", pady=6)

                lbl_name = ctk.CTkLabel(
                    row,
                    text=s_name,
                    font=Theme.font_body_bold(),
                    text_color=colors["text_primary"],
                    width=170,
                    anchor="w"
                )
                lbl_name.pack(side="left")

                bar_frame = ctk.CTkFrame(row, fg_color="transparent")
                bar_frame.pack(side="left", fill="x", expand=True, padx=12)

                bar = ctk.CTkProgressBar(
                    bar_frame,
                    height=10,
                    corner_radius=5,
                    fg_color=colors["bg_card_secondary"],
                    progress_color=s_col
                )
                bar.pack(fill="x")
                bar.set(s_mins / max_mins)

                lbl_val = ctk.CTkLabel(
                    row,
                    text=display_time,
                    font=Theme.font_tag(),
                    text_color=colors["text_secondary"],
                    width=80,
                    anchor="e"
                )
                lbl_val.pack(side="right")

    def _render_bar_chart(self, parent: Any, weekly_data: list):
        colors = Theme.current()
        canvas_h = 170
        canvas_bg = colors["bg_card"]
        
        cv = tk.Canvas(parent, height=canvas_h, bg=canvas_bg, highlightthickness=0)
        cv.pack(fill="x", padx=Theme.CARD_PAD_X, pady=(4, Theme.CARD_PAD_Y))

        def draw():
            cv.delete("all")
            w = cv.winfo_width()
            if w <= 1:
                w = 400
            
            n = len(weekly_data)
            max_val = max([item["minutes"] for item in weekly_data] + [60])
            col_w = w / n
            bar_w = min(40, col_w * 0.55)

            for i, item in enumerate(weekly_data):
                val = item["minutes"]
                cx = i * col_w + col_w / 2
                x1 = cx - bar_w / 2
                x2 = cx + bar_w / 2

                bar_h = (val / max_val) * (canvas_h - 55)
                y2 = canvas_h - 28
                y1 = y2 - max(4, bar_h)

                bar_fill = colors["accent_pink"] if val > 0 else colors["bg_card_secondary"]
                # Rounded bar cap
                cv.create_rectangle(x1, y1, x2, y2, fill=bar_fill, outline="", width=0)

                if val > 0:
                    cv.create_text(cx, y1 - 10, text=f"{val}m", font=(Theme.FONT_HEADING, 9, "bold"), fill=colors["text_secondary"])

                cv.create_text(cx, canvas_h - 12, text=item["day_name"], font=(Theme.FONT_FAMILY, 11), fill=colors["text_primary"])

        cv.bind("<Configure>", lambda e: draw())
        cv.after(40, draw)

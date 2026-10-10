"""
ui/progress_view.py - Modern Progress & Statistics View for Chiikawa Study Planner
Displays task completion rates, study hours, focus sessions, weekly study bar chart, and course distribution.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import date
from typing import Any
from theme import Theme
import database
import assets_mgr


class ProgressView(ctk.CTkFrame):
    """Analytics & progress reporting view with weekly charts and subject distributions."""

    def __init__(self, parent: Any):
        super().__init__(parent, fg_color="transparent")
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        colors = Theme.current()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(16, 12))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Analytics & Progress",
            font=Theme.font_title(),
            text_color=colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Review your study consistency, focus sprint volume, and course allocations.",
            font=Theme.font_body(),
            text_color=colors["text_secondary"]
        ).pack(anchor="w")

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=colors["border_subtle"],
            scrollbar_button_hover_color=colors["accent_pink"]
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
        stat_row.pack(fill="x", pady=(0, 16))
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

        cards_data = [
            ("Task Completion Rate", f"{rate_val}%", colors["accent_pink"], rate_val / 100.0),
            ("Total Study Time", study_time_str, colors["accent_blue"], 0.75),
            ("Study Sessions Logged", f"{pomo_sessions}", colors["accent_yellow"], 0.6),
            ("Consistency Status", "Consistent", colors["accent_mint"], 0.9)
        ]

        for i, (title, val, accent_col, prog) in enumerate(cards_data):
            card = ctk.CTkFrame(
                stat_row,
                fg_color=colors["bg_card"],
                corner_radius=14,
                border_width=1,
                border_color=colors["border"]
            )
            card.grid(row=0, column=i, sticky="nsew", padx=4 if i in (1, 2) else (0 if i == 0 else 4))

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=16, pady=12, fill="both")

            ctk.CTkLabel(inner, text=title, font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=val, font=Theme.font_header(), text_color=colors["text_primary"]).pack(anchor="w", pady=(3, 6))

            bar = ctk.CTkProgressBar(inner, height=5, corner_radius=3, fg_color=colors["bg_card_secondary"], progress_color=accent_col)
            bar.pack(fill="x")
            bar.set(prog)

        # 2. Middle Row: Weekly Study Activity Chart & Mascot Banner
        mid_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        mid_row.pack(fill="x", pady=(0, 16))
        mid_row.grid_columnconfigure(0, weight=7)
        mid_row.grid_columnconfigure(1, weight=3)

        chart_card = ctk.CTkFrame(
            mid_row,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ch_header = ctk.CTkFrame(chart_card, fg_color="transparent")
        ch_header.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(ch_header, text="7-Day Study Activity (Minutes)", font=Theme.font_header(), text_color=colors["text_primary"]).pack(side="left")

        self._render_bar_chart(chart_card, weekly)

        mascot_card = ctk.CTkFrame(
            mid_row,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        mascot_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        m_inner = ctk.CTkFrame(mascot_card, fg_color="transparent")
        m_inner.pack(fill="both", expand=True, padx=16, pady=16)

        grad_img = assets_mgr.get_illustration("graduate", size=(100, 100))
        if grad_img:
            ctk.CTkLabel(m_inner, image=grad_img, text="").pack(pady=(0, 6))

        ctk.CTkLabel(
            m_inner,
            text="Milestone Achievement",
            font=Theme.font_header(),
            text_color=colors["accent_pink"]
        ).pack()

        ctk.CTkLabel(
            m_inner,
            text="'Every minute of focused study brings you closer to mastery!'",
            font=Theme.font_body(),
            text_color=colors["text_secondary"],
            wraplength=170,
            justify="center"
        ).pack(pady=(4, 0))

        # 3. Subject Time Distribution Card
        dist_card = ctk.CTkFrame(
            self.scroll,
            fg_color=colors["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=colors["border"]
        )
        dist_card.pack(fill="x")

        d_header = ctk.CTkFrame(dist_card, fg_color="transparent")
        d_header.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(d_header, text="Study Time Distribution by Course", font=Theme.font_header(), text_color=colors["text_primary"]).pack(side="left")

        d_inner = ctk.CTkFrame(dist_card, fg_color="transparent")
        d_inner.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        if not subject_dist:
            ctk.CTkLabel(d_inner, text="No study sessions recorded yet.", font=Theme.font_small(), text_color=colors["text_secondary"]).pack(anchor="w", pady=6)
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
                row.pack(fill="x", pady=4)

                lbl_name = ctk.CTkLabel(row, text=s_name, font=Theme.font_body_bold(), text_color=colors["text_primary"], width=160, anchor="w")
                lbl_name.pack(side="left")

                bar_frame = ctk.CTkFrame(row, fg_color="transparent")
                bar_frame.pack(side="left", fill="x", expand=True, padx=10)

                bar = ctk.CTkProgressBar(bar_frame, height=8, corner_radius=4, fg_color=colors["bg_card_secondary"], progress_color=s_col)
                bar.pack(fill="x")
                bar.set(s_mins / max_mins)

                lbl_val = ctk.CTkLabel(row, text=display_time, font=Theme.font_tag(), text_color=colors["text_secondary"], width=70, anchor="e")
                lbl_val.pack(side="right")

    def _render_bar_chart(self, parent: Any, weekly_data: list):
        colors = Theme.current()
        canvas_h = 160
        canvas_bg = colors["bg_card"]
        
        cv = tk.Canvas(parent, height=canvas_h, bg=canvas_bg, highlightthickness=0)
        cv.pack(fill="x", padx=16, pady=(4, 14))

        def draw():
            cv.delete("all")
            w = cv.winfo_width()
            if w <= 1:
                w = 400
            
            n = len(weekly_data)
            max_val = max([item["minutes"] for item in weekly_data] + [60])
            col_w = w / n
            bar_w = min(36, col_w * 0.55)

            for i, item in enumerate(weekly_data):
                val = item["minutes"]
                cx = i * col_w + col_w / 2
                x1 = cx - bar_w / 2
                x2 = cx + bar_w / 2

                bar_h = (val / max_val) * (canvas_h - 50)
                y2 = canvas_h - 26
                y1 = y2 - max(4, bar_h)

                bar_fill = colors["accent_pink"] if val > 0 else colors["bg_card_secondary"]
                cv.create_rectangle(x1, y1, x2, y2, fill=bar_fill, outline="", width=0)

                if val > 0:
                    cv.create_text(cx, y1 - 8, text=f"{val}m", font=("Segoe UI", 8, "bold"), fill=colors["text_secondary"])

                cv.create_text(cx, canvas_h - 12, text=item["day_name"], font=("Segoe UI", 9), fill=colors["text_primary"])

        cv.bind("<Configure>", lambda e: draw())
        cv.after(40, draw)

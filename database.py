"""
database.py - SQLite storage for Chiikawa Study Planner
Manages database initialization, schema migration, and CRUD operations.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chiikawa_study.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Create all required tables and default records if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Subjects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#FF8FB1',
                icon TEXT DEFAULT '📚',
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
        """)

        # Tasks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
                category TEXT DEFAULT 'Study',
                priority TEXT DEFAULT 'Medium',
                due_date TEXT,
                due_time TEXT DEFAULT '23:59',
                task_type TEXT DEFAULT 'daily',
                completed INTEGER DEFAULT 0,
                completed_at TEXT,
                created_at TEXT NOT NULL
            );
        """)

        # Sticky notes for Interactive Corkboard
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sticky_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT DEFAULT 'Note',
                content TEXT NOT NULL,
                color TEXT DEFAULT '#FFEAA7',
                x INTEGER DEFAULT 60,
                y INTEGER DEFAULT 60,
                date_tag TEXT,
                created_at TEXT NOT NULL
            );
        """)

        # Calendar events & deadlines
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                event_type TEXT DEFAULT 'Event',
                subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
                start_date TEXT NOT NULL,
                start_time TEXT DEFAULT '09:00',
                end_date TEXT,
                end_time TEXT DEFAULT '10:00',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
        """)

        # Study sessions (Pomodoro / tracked study time)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
                topic TEXT DEFAULT 'General Study',
                duration_minutes INTEGER NOT NULL,
                session_type TEXT DEFAULT 'Pomodoro',
                date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
        """)

        # Habits
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'Study',
                target_frequency TEXT DEFAULT 'Daily',
                icon TEXT DEFAULT '⭐',
                created_at TEXT NOT NULL
            );
        """)

        # Habit daily logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                date TEXT NOT NULL,
                completed INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                UNIQUE(habit_id, date)
            );
        """)

        # Notes & Quick Capture
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
                category TEXT DEFAULT 'General',
                pinned INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        # Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

        # Default settings if not set
        defaults = {
            "theme_mode": "light",        # light / dark
            "pomodoro_focus": "25",       # minutes
            "pomodoro_short_break": "5",
            "pomodoro_long_break": "15",
            "user_name": "Chiikawa Friend",
            "sound_enabled": "1"
        }
        for k, v in defaults.items():
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);", (k, v))

        # Schema migration: ensure tasks table has task_type column
        cursor.execute("PRAGMA table_info(tasks);")
        task_cols = [col[1] for col in cursor.fetchall()]
        if "task_type" not in task_cols:
            cursor.execute("ALTER TABLE tasks ADD COLUMN task_type TEXT DEFAULT 'daily';")

        # Schema migration: ensure event_categories table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL,
                is_default INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
        """)
        cursor.execute("SELECT COUNT(*) as count FROM event_categories;")
        if cursor.fetchone()["count"] == 0:
            now_iso = datetime.now().isoformat()
            default_categories = [
                ("Exams", "#FF7597", 1),
                ("Assignments", "#5B9BD5", 1),
                ("Study Sessions", "#42B883", 1),
                ("Deadlines", "#F5A623", 1),
                ("Personal", "#9A7BD6", 1),
                ("Other", "#F08CBA", 1),
            ]
            for cat_name, cat_color, is_def in default_categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO event_categories (name, color, is_default, created_at)
                    VALUES (?, ?, ?, ?);
                """, (cat_name, cat_color, is_def, now_iso))

        # Schema migration: ensure calendar_events table has color, location, category, reminder, recurring columns
        cursor.execute("PRAGMA table_info(calendar_events);")
        ev_cols = [col[1] for col in cursor.fetchall()]
        if "color" not in ev_cols:
            cursor.execute("ALTER TABLE calendar_events ADD COLUMN color TEXT DEFAULT '';")
        if "location" not in ev_cols:
            cursor.execute("ALTER TABLE calendar_events ADD COLUMN location TEXT DEFAULT '';")
        if "category" not in ev_cols:
            cursor.execute("ALTER TABLE calendar_events ADD COLUMN category TEXT DEFAULT '';")
        if "reminder" not in ev_cols:
            cursor.execute("ALTER TABLE calendar_events ADD COLUMN reminder TEXT DEFAULT 'None';")
        if "recurring" not in ev_cols:
            cursor.execute("ALTER TABLE calendar_events ADD COLUMN recurring TEXT DEFAULT 'None';")

        cursor.execute("""
            UPDATE calendar_events
            SET category = event_type
            WHERE category IS NULL OR category = '';
        """)

        conn.commit()

        # Seed sample data if subjects is empty
        cursor.execute("SELECT COUNT(*) as count FROM subjects;")
        if cursor.fetchone()["count"] == 0:
            seed_sample_data(conn)


def seed_sample_data(conn: Optional[sqlite3.Connection] = None) -> None:
    """Populate default subjects, tasks, habits, sticky notes, and events."""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    try:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        today = date.today()
        today_str = today.isoformat()
        tomorrow_str = (today + timedelta(days=1)).isoformat()
        in_3_days_str = (today + timedelta(days=3)).isoformat()
        in_5_days_str = (today + timedelta(days=5)).isoformat()

        # Default subjects
        subjects = [
            ("Computer Science", "#88CDF6", "💻", "Algorithms, Data Structures & Python"),
            ("Mathematics", "#FF8FB1", "📐", "Calculus, Linear Algebra & Discrete Math"),
            ("English Literature", "#FFEAA7", "📖", "Readings, Essays and Term Papers"),
            ("Biology", "#A8E6CF", "🌱", "Genetics, Cell Biology & Lab reports"),
            ("Art & Design", "#D4C5F9", "🎨", "Sketching, UI/UX and Pastel Aesthetics")
        ]
        for name, color, icon, desc in subjects:
            cursor.execute(
                "INSERT OR IGNORE INTO subjects (name, color, icon, description, created_at) VALUES (?, ?, ?, ?, ?);",
                (name, color, icon, desc, now_str)
            )

        # Get subject IDs
        cursor.execute("SELECT id, name FROM subjects;")
        sub_map = {row["name"]: row["id"] for row in cursor.fetchall()}

        # Default tasks
        sample_tasks = [
            ("Review Python Data Structures", "Practice trees and hash maps for upcoming exam", sub_map.get("Computer Science"), "Study", "High", today_str, "16:00", 0),
            ("Calculus Problem Set #4", "Complete odd problems 1 to 25 in Chapter 3", sub_map.get("Mathematics"), "Homework", "Medium", today_str, "18:00", 0),
            ("Read Chapter 5 of Literature Book", "Write 2-paragraph summary on character development", sub_map.get("English Literature"), "Reading", "Low", tomorrow_str, "20:00", 0),
            ("Prepare Biology Presentation Slides", "Include cell division diagrams and Chiikawa stickers", sub_map.get("Biology"), "Exam Prep", "High", in_3_days_str, "14:00", 0),
            ("Clean Desk & Organize Study Station", "Neat room, peaceful mind! Yaha!", None, "Personal", "Low", today_str, "12:00", 1),
        ]
        for title, desc, s_id, cat, prio, d_date, d_time, comp in sample_tasks:
            comp_at = now_str if comp else None
            cursor.execute("""
                INSERT INTO tasks (title, description, subject_id, category, priority, due_date, due_time, completed, completed_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (title, desc, s_id, cat, prio, d_date, d_time, comp, comp_at, now_str))

        # Default Sticky Notes for Corkboard
        notes = [
            ("Welcome to Planner! 💖", "Chiikawa, Hachiware, and Usagi are here to cheer you on! Keep doing your best! Yaha!", "#FFEAA7", 50, 40, today_str),
            ("Exam Reminder 🔔", "Midterm exams start next week! Don't forget to review summary sheets.", "#FF8FB1", 330, 60, in_5_days_str),
            ("Study Tip ☕", "Take 5 min breaks every 25 mins. Drink warm tea or strawberry milk!", "#A8E6CF", 70, 260, today_str),
            ("Formula Note 📐", "Euler's formula: e^(i*pi) + 1 = 0.\nRemember integrals of sin and cos!", "#D4C5F9", 350, 280, tomorrow_str)
        ]
        for title, content, color, x, y, d_tag in notes:
            cursor.execute("""
                INSERT INTO sticky_notes (title, content, color, x, y, date_tag, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (title, content, color, x, y, d_tag, now_str))

        # Default Habits
        sample_habits = [
            ("Read 20 pages of coursebook", "Study", "Daily", "📖"),
            ("Complete 1 Pomodoro session", "Study", "Daily", "⏱️"),
            ("Drink 2L of water", "Health", "Daily", "💧"),
            ("Review daily lecture notes", "Review", "Daily", "📝"),
            ("Sleep before 11:30 PM", "Health", "Daily", "🌙")
        ]
        for title, cat, freq, icon in sample_habits:
            cursor.execute("""
                INSERT INTO habits (title, category, target_frequency, icon, created_at)
                VALUES (?, ?, ?, ?, ?);
            """, (title, cat, freq, icon, now_str))

        # Seed habit completions for past 3 days
        cursor.execute("SELECT id FROM habits;")
        habit_ids = [row["id"] for row in cursor.fetchall()]
        for hid in habit_ids:
            for day_offset in [1, 2]:
                past_date = (today - timedelta(days=day_offset)).isoformat()
                cursor.execute("""
                    INSERT OR IGNORE INTO habit_logs (habit_id, date, completed, created_at)
                    VALUES (?, ?, 1, ?);
                """, (hid, past_date, now_str))

        # Default Calendar Events
        events = [
            ("CS Lab Workshop", "Event", sub_map.get("Computer Science"), today_str, "10:00", today_str, "12:00", "Lab room 302"),
            ("Calculus Midterm Review", "Exam", sub_map.get("Mathematics"), tomorrow_str, "14:00", tomorrow_str, "16:00", "Bring graphic calculator"),
            ("Biology Group Project Due", "Assignment", sub_map.get("Biology"), in_3_days_str, "23:59", in_3_days_str, "23:59", "Upload PDF to portal"),
            ("Chiikawa Study Tea Party 🍰", "Event", None, in_5_days_str, "15:00", in_5_days_str, "17:00", "Reward session after hard work!")
        ]
        for title, etype, sid, sdate, stime, edate, etime, notes_txt in events:
            cursor.execute("""
                INSERT INTO calendar_events (title, event_type, subject_id, start_date, start_time, end_date, end_time, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (title, etype, sid, sdate, stime, edate, etime, notes_txt, now_str))

        # Default Notes
        lecture_notes = [
            ("Quick Lecture Capture: Algorithmic Complexity", "Big-O notation describes limiting behavior of functions.\nO(1): constant\nO(log n): binary search\nO(n): linear scan\nO(n log n): merge sort / quicksort", sub_map.get("Computer Science"), "Lecture", 1),
            ("Favorite Quotes & Encouragements", "'Wakannai kedo, nantoka nare!' (I don't really know, but somehow it'll work out! - Chiikawa)\nKeep going even when things seem tough! 🌸", None, "Inspiration", 1),
            ("Essay Outline Ideas", "Intro: The impact of industrialization.\nBody 1: Economic shifts.\nBody 2: Societal transformations.\nConclusion: Modern parallels.", sub_map.get("English Literature"), "Draft", 0)
        ]
        for title, content, sid, cat, pin in lecture_notes:
            cursor.execute("""
                INSERT INTO notes (title, content, subject_id, category, pinned, updated_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (title, content, sid, cat, pin, now_str, now_str))

        # Sample Study Sessions
        sessions = [
            (sub_map.get("Computer Science"), "Algorithm practice", 50, "Pomodoro", today_str, "Finished 2 medium tasks"),
            (sub_map.get("Mathematics"), "Calculus Chapter 3", 45, "Pomodoro", (today - timedelta(days=1)).isoformat(), "Reviewed limits"),
            (sub_map.get("Biology"), "Cell structures review", 25, "Pomodoro", (today - timedelta(days=2)).isoformat(), "Flashcards run"),
        ]
        for sid, top, dur, stype, sdate, snotes in sessions:
            cursor.execute("""
                INSERT INTO study_sessions (subject_id, topic, duration_minutes, session_type, date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (sid, top, dur, stype, sdate, snotes, now_str))

        conn.commit()
    finally:
        if should_close:
            conn.close()


# -------------------------------------------------------------
# CRUD: Subjects
# -------------------------------------------------------------
def get_all_subjects() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects ORDER BY name ASC;")
        return [dict(r) for r in cursor.fetchall()]


def add_subject(name: str, color: str = "#FF8FB1", icon: str = "📚", description: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO subjects (name, color, icon, description, created_at) VALUES (?, ?, ?, ?, ?);",
            (name, color, icon, description, now_str)
        )
        conn.commit()
        return cursor.lastrowid


def update_subject(subject_id: int, name: str, color: str, icon: str, description: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subjects SET name = ?, color = ?, icon = ?, description = ? WHERE id = ?;",
            (name, color, icon, description, subject_id)
        )
        conn.commit()


def delete_subject(subject_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id = ?;", (subject_id,))
        conn.commit()


# -------------------------------------------------------------
# CRUD: Tasks
# -------------------------------------------------------------
def get_tasks(
    filter_status: str = "all",       # all, active, completed
    subject_id: Optional[int] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    search_query: Optional[str] = None,
    task_type: Optional[str] = None   # daily, general, or None (all)
) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT t.*, s.name as subject_name, s.color as subject_color, s.icon as subject_icon
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE 1=1
        """
        params = []

        if filter_status == "active":
            query += " AND t.completed = 0"
        elif filter_status == "completed":
            query += " AND t.completed = 1"

        if subject_id:
            query += " AND t.subject_id = ?"
            params.append(subject_id)

        if category and category != "All":
            query += " AND t.category = ?"
            params.append(category)

        if priority and priority != "All":
            query += " AND t.priority = ?"
            params.append(priority)

        if due_date:
            query += " AND t.due_date = ?"
            params.append(due_date)

        if task_type:
            if task_type == "daily":
                query += " AND (t.task_type = 'daily' OR t.task_type IS NULL)"
            else:
                query += " AND t.task_type = ?"
                params.append(task_type)

        if search_query:
            query += " AND (t.title LIKE ? OR t.description LIKE ?)"
            like_str = f"%{search_query}%"
            params.extend([like_str, like_str])

        query += " ORDER BY t.completed ASC, t.due_date ASC, t.priority DESC, t.id DESC;"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]


def add_task(
    title: str,
    description: str = "",
    subject_id: Optional[int] = None,
    category: str = "Study",
    priority: str = "Medium",
    due_date: Optional[str] = None,
    due_time: str = "23:59",
    task_type: str = "daily"
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO tasks (title, description, subject_id, category, priority, due_date, due_time, task_type, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?);
        """, (title, description, subject_id, category, priority, due_date, due_time, task_type, now_str))
        conn.commit()
        return cursor.lastrowid


def update_task(
    task_id: int,
    title: str,
    description: str,
    subject_id: Optional[int],
    category: str,
    priority: str,
    due_date: Optional[str],
    due_time: str,
    task_type: Optional[str] = None
) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        if task_type is not None:
            cursor.execute("""
                UPDATE tasks
                SET title = ?, description = ?, subject_id = ?, category = ?, priority = ?, due_date = ?, due_time = ?, task_type = ?
                WHERE id = ?;
            """, (title, description, subject_id, category, priority, due_date, due_time, task_type, task_id))
        else:
            cursor.execute("""
                UPDATE tasks
                SET title = ?, description = ?, subject_id = ?, category = ?, priority = ?, due_date = ?, due_time = ?
                WHERE id = ?;
            """, (title, description, subject_id, category, priority, due_date, due_time, task_id))
        conn.commit()


def toggle_task_completed(task_id: int, completed: bool) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        comp_int = 1 if completed else 0
        comp_at = datetime.now().isoformat() if completed else None
        cursor.execute("UPDATE tasks SET completed = ?, completed_at = ? WHERE id = ?;", (comp_int, comp_at, task_id))
        conn.commit()


def delete_task(task_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
        conn.commit()


# -------------------------------------------------------------
# CRUD: Sticky Notes (Corkboard)
# -------------------------------------------------------------
def get_all_sticky_notes() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sticky_notes ORDER BY id ASC;")
        return [dict(r) for r in cursor.fetchall()]


def add_sticky_note(
    title: str = "Note",
    content: str = "",
    color: str = "#FFEAA7",
    x: int = 50,
    y: int = 50,
    date_tag: Optional[str] = None
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO sticky_notes (title, content, color, x, y, date_tag, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (title, content, color, x, y, date_tag, now_str))
        conn.commit()
        return cursor.lastrowid


def update_sticky_note_position(note_id: int, x: int, y: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE sticky_notes SET x = ?, y = ? WHERE id = ?;", (x, y, note_id))
        conn.commit()


def update_sticky_note_content(note_id: int, title: str, content: str, color: str, date_tag: Optional[str] = None) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sticky_notes SET title = ?, content = ?, color = ?, date_tag = ? WHERE id = ?;
        """, (title, content, color, date_tag, note_id))
        conn.commit()


def delete_sticky_note(note_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sticky_notes WHERE id = ?;", (note_id,))
        conn.commit()


# -------------------------------------------------------------
# CRUD: Calendar Events & Categories
# -------------------------------------------------------------
def get_event_categories() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM event_categories ORDER BY id ASC;")
        rows = [dict(r) for r in cursor.fetchall()]
        if not rows:
            return [
                {"id": 1, "name": "Exams", "color": "#FF7597", "is_default": 1},
                {"id": 2, "name": "Assignments", "color": "#5B9BD5", "is_default": 1},
                {"id": 3, "name": "Study Sessions", "color": "#42B883", "is_default": 1},
                {"id": 4, "name": "Deadlines", "color": "#F5A623", "is_default": 1},
                {"id": 5, "name": "Personal", "color": "#9A7BD6", "is_default": 1},
                {"id": 6, "name": "Other", "color": "#F08CBA", "is_default": 1},
            ]
        return rows


def get_category_color(category_name: str) -> str:
    if not category_name:
        return "#FF7597"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT color FROM event_categories WHERE LOWER(name) = LOWER(?);", (category_name.strip(),))
        row = cursor.fetchone()
        if row and row["color"]:
            return row["color"]
    default_colors = {
        "exam": "#FF7597",
        "exams": "#FF7597",
        "assignment": "#5B9BD5",
        "assignments": "#5B9BD5",
        "study session": "#42B883",
        "study sessions": "#42B883",
        "deadline": "#F5A623",
        "deadlines": "#F5A623",
        "personal": "#9A7BD6",
        "event": "#F08CBA",
        "other": "#F08CBA",
    }
    return default_colors.get(category_name.lower().strip(), "#FF7597")


def add_event_category(name: str, color: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO event_categories (name, color, is_default, created_at)
            VALUES (?, ?, 0, ?);
        """, (name.strip(), color.strip(), now_str))
        conn.commit()
        return cursor.lastrowid


def update_event_category(cat_id: int, name: str, color: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM event_categories WHERE id = ?;", (cat_id,))
        old = cursor.fetchone()
        old_name = old["name"] if old else None

        cursor.execute("""
            UPDATE event_categories
            SET name = ?, color = ?
            WHERE id = ?;
        """, (name.strip(), color.strip(), cat_id))

        if old_name:
            cursor.execute("""
                UPDATE calendar_events
                SET category = ?, color = ?
                WHERE category = ?;
            """, (name.strip(), color.strip(), old_name))
        conn.commit()


def rename_event_category(cat_id: int, new_name: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT color FROM event_categories WHERE id = ?;", (cat_id,))
        row = cursor.fetchone()
        color = row["color"] if row else "#FF7597"
        update_event_category(cat_id, new_name, color)


def delete_event_category(cat_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM event_categories WHERE id = ?;", (cat_id,))
        row = cursor.fetchone()
        if not row:
            return False
        cat_name = row["name"]

        cursor.execute("""
            UPDATE calendar_events
            SET category = 'Other', color = '#F08CBA'
            WHERE category = ?;
        """, (cat_name,))

        cursor.execute("DELETE FROM event_categories WHERE id = ?;", (cat_id,))
        conn.commit()
        return True


def get_contrast_text_color(hex_color: str) -> str:
    """Returns #FFFFFF or #2D2630 based on perceived luminance of the background hex."""
    try:
        c = hex_color.lstrip("#")
        if len(c) == 6:
            r = int(c[0:2], 16)
            g = int(c[2:4], 16)
            b = int(c[4:6], 16)
            lum = (r * 299 + g * 587 + b * 114) / 1000
            return "#2D2630" if lum > 165 else "#FFFFFF"
    except Exception:
        pass
    return "#FFFFFF"


def get_calendar_events(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT e.*, s.name as subject_name, s.color as subject_color
            FROM calendar_events e
            LEFT JOIN subjects s ON e.subject_id = s.id
            WHERE 1=1
        """
        params = []
        if start_date and end_date:
            query += " AND (e.start_date BETWEEN ? AND ? OR e.end_date BETWEEN ? AND ?)"
            params.extend([start_date, end_date, start_date, end_date])
        elif start_date:
            query += " AND e.start_date >= ?"
            params.append(start_date)

        query += " ORDER BY e.start_date ASC, e.start_time ASC;"
        cursor.execute(query, params)
        events = [dict(r) for r in cursor.fetchall()]
        for ev in events:
            if not ev.get("category"):
                ev["category"] = ev.get("event_type", "Event")
            if not ev.get("color"):
                ev["color"] = get_category_color(ev["category"])
        return events


def add_calendar_event(
    title: str,
    event_type: str = "Event",
    subject_id: Optional[int] = None,
    start_date: str = "",
    start_time: str = "09:00",
    end_date: Optional[str] = None,
    end_time: str = "10:00",
    notes: str = "",
    color: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None,
    reminder: Optional[str] = "None",
    recurring: Optional[str] = "None"
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cat_val = category or event_type or "Event"
        color_val = color or get_category_color(cat_val)
        loc_val = location or ""
        rem_val = reminder or "None"
        rec_val = recurring or "None"
        cursor.execute("""
            INSERT INTO calendar_events (title, event_type, subject_id, start_date, start_time, end_date, end_time, notes, color, location, category, reminder, recurring, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (title, event_type, subject_id, start_date, start_time, end_date or start_date, end_time, notes, color_val, loc_val, cat_val, rem_val, rec_val, now_str))
        conn.commit()
        return cursor.lastrowid


def delete_calendar_event(event_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM calendar_events WHERE id = ?;", (event_id,))
        conn.commit()


def update_calendar_event(
    event_id: int,
    title: str,
    event_type: str = "Event",
    subject_id: Optional[int] = None,
    start_date: str = "",
    start_time: str = "09:00",
    end_date: Optional[str] = None,
    end_time: str = "10:00",
    notes: str = "",
    color: Optional[str] = None,
    location: Optional[str] = None,
    category: Optional[str] = None,
    reminder: Optional[str] = "None",
    recurring: Optional[str] = "None"
) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cat_val = category or event_type or "Event"
        color_val = color or get_category_color(cat_val)
        loc_val = location if location is not None else ""
        rem_val = reminder or "None"
        rec_val = recurring or "None"
        cursor.execute("""
            UPDATE calendar_events
            SET title = ?, event_type = ?, subject_id = ?, start_date = ?, start_time = ?, end_date = ?, end_time = ?, notes = ?, color = ?, location = ?, category = ?, reminder = ?, recurring = ?
            WHERE id = ?;
        """, (title, event_type, subject_id, start_date, start_time, end_date or start_date, end_time, notes, color_val, loc_val, cat_val, rem_val, rec_val, event_id))
        conn.commit()


def duplicate_calendar_event(event_id: int, new_date: Optional[str] = None) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calendar_events WHERE id = ?;", (event_id,))
        row = cursor.fetchone()
        if not row:
            return None
        ev = dict(row)
        target_date = new_date or ev["start_date"]
        target_end_date = new_date or ev.get("end_date") or target_date
        return add_calendar_event(
            title=f"{ev['title']} (Copy)" if not new_date else ev['title'],
            event_type=ev.get("event_type", "Event"),
            subject_id=ev.get("subject_id"),
            start_date=target_date,
            start_time=ev.get("start_time", "09:00"),
            end_date=target_end_date,
            end_time=ev.get("end_time", "10:00"),
            notes=ev.get("notes", ""),
            color=ev.get("color"),
            location=ev.get("location", ""),
            category=ev.get("category", ev.get("event_type", "Event")),
            reminder=ev.get("reminder", "None"),
            recurring=ev.get("recurring", "None")
        )


# -------------------------------------------------------------
# CRUD: Study Sessions (Pomodoro Tracking)
# -------------------------------------------------------------
def log_study_session(
    subject_id: Optional[int],
    topic: str,
    duration_minutes: int,
    session_type: str = "Pomodoro",
    session_date: Optional[str] = None,
    notes: str = ""
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        date_str = session_date or date.today().isoformat()
        cursor.execute("""
            INSERT INTO study_sessions (subject_id, topic, duration_minutes, session_type, date, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (subject_id, topic, duration_minutes, session_type, date_str, notes, now_str))
        conn.commit()
        return cursor.lastrowid


def get_study_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ss.*, s.name as subject_name, s.color as subject_color
            FROM study_sessions ss
            LEFT JOIN subjects s ON ss.subject_id = s.id
            ORDER BY ss.date DESC, ss.id DESC
            LIMIT ?;
        """, (limit,))
        return [dict(r) for r in cursor.fetchall()]


def delete_study_session(session_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_sessions WHERE id = ?;", (session_id,))
        conn.commit()


# -------------------------------------------------------------
# CRUD: Habits & Habit Logs
# -------------------------------------------------------------
def get_all_habits() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM habits ORDER BY id ASC;")
        return [dict(r) for r in cursor.fetchall()]


def add_habit(title: str, category: str = "Study", target_frequency: str = "Daily", icon: str = "⭐") -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO habits (title, category, target_frequency, icon, created_at)
            VALUES (?, ?, ?, ?, ?);
        """, (title, category, target_frequency, icon, now_str))
        conn.commit()
        return cursor.lastrowid


def delete_habit(habit_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habits WHERE id = ?;", (habit_id,))
        conn.commit()


def toggle_habit_date(habit_id: int, log_date: str) -> bool:
    """Toggles habit completion for given date. Returns new status (True/False)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM habit_logs WHERE habit_id = ? AND date = ?;", (habit_id, log_date))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("DELETE FROM habit_logs WHERE id = ?;", (existing["id"],))
            conn.commit()
            return False
        else:
            now_str = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO habit_logs (habit_id, date, completed, created_at)
                VALUES (?, ?, 1, ?);
            """, (habit_id, log_date, now_str))
            conn.commit()
            return True


def get_habit_logs_for_range(start_date: str, end_date: str) -> Dict[int, set]:
    """Returns {habit_id: set_of_dates_completed}."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT habit_id, date FROM habit_logs
            WHERE date BETWEEN ? AND ?;
        """, (start_date, end_date))
        result: Dict[int, set] = {}
        for row in cursor.fetchall():
            hid = row["habit_id"]
            if hid not in result:
                result[hid] = set()
            result[hid].add(row["date"])
        return result


def get_habit_streak(habit_id: int) -> Dict[str, int]:
    """Calculates current streak and best streak for a habit."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM habit_logs WHERE habit_id = ? ORDER BY date DESC;", (habit_id,))
        dates = [datetime.strptime(r["date"], "%Y-%m-%d").date() for r in cursor.fetchall()]

        if not dates:
            return {"current": 0, "best": 0, "total": 0}

        total = len(dates)
        date_set = set(dates)

        # Current streak
        current_streak = 0
        check_date = date.today()
        # If not done today, check if done yesterday to keep streak alive
        if check_date not in date_set:
            check_date -= timedelta(days=1)

        while check_date in date_set:
            current_streak += 1
            check_date -= timedelta(days=1)

        # Best streak
        sorted_dates = sorted(list(date_set))
        best_streak = 0
        curr_streak_counter = 0
        prev_d = None
        for d in sorted_dates:
            if prev_d is None or d == prev_d + timedelta(days=1):
                curr_streak_counter += 1
            else:
                curr_streak_counter = 1
            if curr_streak_counter > best_streak:
                best_streak = curr_streak_counter
            prev_d = d

        return {"current": current_streak, "best": best_streak, "total": total}


# -------------------------------------------------------------
# CRUD: Notes & Quick Capture
# -------------------------------------------------------------
def get_notes(search_query: Optional[str] = None, subject_id: Optional[int] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT n.*, s.name as subject_name, s.color as subject_color
            FROM notes n
            LEFT JOIN subjects s ON n.subject_id = s.id
            WHERE 1=1
        """
        params = []
        if subject_id:
            query += " AND n.subject_id = ?"
            params.append(subject_id)
        if search_query:
            query += " AND (n.title LIKE ? OR n.content LIKE ?)"
            like_s = f"%{search_query}%"
            params.extend([like_s, like_s])

        query += " ORDER BY n.pinned DESC, n.updated_at DESC;"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]


def add_note(title: str, content: str, subject_id: Optional[int] = None, category: str = "General", pinned: int = 0) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO notes (title, content, subject_id, category, pinned, updated_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (title, content, subject_id, category, pinned, now_str, now_str))
        conn.commit()
        return cursor.lastrowid


def update_note(note_id: int, title: str, content: str, subject_id: Optional[int], category: str, pinned: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute("""
            UPDATE notes
            SET title = ?, content = ?, subject_id = ?, category = ?, pinned = ?, updated_at = ?
            WHERE id = ?;
        """, (title, content, subject_id, category, pinned, now_str, note_id))
        conn.commit()


def delete_note(note_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?;", (note_id,))
        conn.commit()


# -------------------------------------------------------------
# Statistics & Progress aggregations
# -------------------------------------------------------------
def get_dashboard_stats() -> Dict[str, Any]:
    today_str = date.today().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()

        # Today's tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE due_date = ?;", (today_str,))
        today_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE due_date = ? AND completed = 1;", (today_str,))
        today_completed = cursor.fetchone()[0]

        # Total tasks
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        all_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1;")
        all_completed = cursor.fetchone()[0]

        # Total study minutes today
        cursor.execute("SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions WHERE date = ?;", (today_str,))
        study_minutes_today = cursor.fetchone()[0]

        # Total study minutes all time
        cursor.execute("SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions;")
        study_minutes_total = cursor.fetchone()[0]

        # Upcoming deadlines (next 7 days)
        in_7_days = (date.today() + timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT t.*, s.name as subject_name, s.color as subject_color
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.completed = 0 AND t.due_date BETWEEN ? AND ?
            ORDER BY t.due_date ASC, t.due_time ASC;
        """, (today_str, in_7_days))
        upcoming_tasks = [dict(r) for r in cursor.fetchall()]

        # Upcoming exams or assignments
        cursor.execute("""
            SELECT e.*, s.name as subject_name, s.color as subject_color
            FROM calendar_events e
            LEFT JOIN subjects s ON e.subject_id = s.id
            WHERE e.start_date BETWEEN ? AND ?
            ORDER BY e.start_date ASC, e.start_time ASC;
        """, (today_str, in_7_days))
        upcoming_events = [dict(r) for r in cursor.fetchall()]

        rate = int((today_completed / today_total) * 100) if today_total > 0 else 0
        overall_rate = int((all_completed / all_total) * 100) if all_total > 0 else 0

        return {
            "today_total": today_total,
            "today_completed": today_completed,
            "today_rate": rate,
            "all_total": all_total,
            "all_completed": all_completed,
            "overall_rate": overall_rate,
            "study_minutes_today": study_minutes_today,
            "study_minutes_total": study_minutes_total,
            "upcoming_tasks": upcoming_tasks,
            "upcoming_events": upcoming_events
        }


def get_weekly_study_stats() -> List[Dict[str, Any]]:
    """Returns study minutes per day for the last 7 days."""
    today = date.today()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    result = []
    with get_connection() as conn:
        cursor = conn.cursor()
        for d in days:
            d_str = d.isoformat()
            cursor.execute("SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions WHERE date = ?;", (d_str,))
            minutes = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed_at LIKE ?;", (f"{d_str}%",))
            completed_tasks = cursor.fetchone()[0]
            result.append({
                "date": d_str,
                "day_name": d.strftime("%a"),
                "minutes": minutes,
                "tasks": completed_tasks
            })
    return result


def get_subject_time_distribution() -> List[Dict[str, Any]]:
    """Returns minutes spent per subject."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(s.name, 'General') as subject_name,
                   COALESCE(s.color, '#FF8FB1') as subject_color,
                   SUM(ss.duration_minutes) as total_minutes
            FROM study_sessions ss
            LEFT JOIN subjects s ON ss.subject_id = s.id
            GROUP BY ss.subject_id
            ORDER BY total_minutes DESC;
        """)
        return [dict(r) for r in cursor.fetchall()]


# -------------------------------------------------------------
# Settings CRUD
# -------------------------------------------------------------
def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", (key, value))
        conn.commit()


def reset_database() -> None:
    """Drops and recreates all tables, resetting to sample state."""
    with get_connection() as conn:
        cursor = conn.cursor()
        tables = ["habit_logs", "habits", "study_sessions", "calendar_events", "sticky_notes", "tasks", "notes", "subjects", "settings"]
        for t in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {t};")
        conn.commit()
    init_db()

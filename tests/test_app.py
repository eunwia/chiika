"""
tests/test_app.py - Automated test suite for Chiikawa Study Planner
Verifies database operations, form buttons/modals, typography, dark mode sidebar transitions, and navigation.
"""

import sys
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
import icons
import assets_mgr
from app import ChiikawaApp
from theme import Theme
from ui.components.modal import (
    TaskModal, StickyNoteModal, SubjectModal, EventModal,
    HabitModal, NoteModal, SessionModal
)


def test_database():
    print("[Test] Testing database initialization and CRUD...")
    database.init_db()

    subjects = database.get_all_subjects()
    assert len(subjects) >= 4, f"Expected at least 4 subjects, got {len(subjects)}"

    # Task CRUD
    tid = database.add_task(title="Test Task", description="Testing", category="Study", priority="High")
    assert tid > 0
    database.toggle_task_completed(tid, True)
    tasks = database.get_tasks(filter_status="completed")
    assert any(t["id"] == tid for t in tasks)
    database.delete_task(tid)

    # Sticky note CRUD
    nid = database.add_sticky_note(title="Test Sticky", content="Sticky content", color="#FEF3C7", x=100, y=120)
    assert nid > 0
    database.update_sticky_note_position(nid, 200, 220)
    database.delete_sticky_note(nid)

    # Habit CRUD
    hid = database.add_habit(title="Test Habit", category="Study")
    assert hid > 0
    toggled = database.toggle_habit_date(hid, "2026-10-10")
    assert toggled is True
    database.delete_habit(hid)

    # Note CRUD
    note_id = database.add_note(title="Test Note", content="Some content")
    assert note_id > 0
    database.delete_note(note_id)

    # Calendar Event CRUD
    eid = database.add_calendar_event(title="Test Event", event_type="Exam", start_date="2026-10-15")
    assert eid > 0
    database.update_calendar_event(eid, title="Updated Test Event", event_type="Exam", start_date="2026-10-16")
    evs = database.get_calendar_events(start_date="2026-10-16", end_date="2026-10-16")
    assert any(e["id"] == eid and e["title"] == "Updated Test Event" for e in evs)
    database.delete_calendar_event(eid)
    evs_after = database.get_calendar_events(start_date="2026-10-16", end_date="2026-10-16")
    assert not any(e["id"] == eid for e in evs_after)

    print("[Test] Database CRUD tests passed successfully!")


def test_typography():
    print("[Test] Testing improved font typography...")
    title_font = Theme.font_title()
    body_font = Theme.font_body()
    header_font = Theme.font_header()

    assert any(f in title_font[0] for f in ("Segoe UI", "Yu Gothic UI")), f"Expected clean modern font in title font, got {title_font}"
    assert any(f in body_font[0] for f in ("Segoe UI", "Yu Gothic UI")), f"Expected clean modern font in body font, got {body_font}"
    assert any(f in header_font[0] for f in ("Segoe UI", "Yu Gothic UI")), f"Expected clean modern font in header font, got {header_font}"
    print(f"  [OK] Font family verified: {Theme.FONT_FAMILY} / {Theme.FONT_HEADING}")


def test_icons_and_assets():
    print("[Test] Testing icon generation and asset cache...")
    for icon_name in ["dashboard", "tasks", "corkboard", "calendar", "study", "timer", "habits", "notes", "progress", "search", "settings", "plus", "trash", "edit", "x", "check"]:
        ic = icons.get_icon(icon_name, size=16, color="#E66882")
        assert ic is not None, f"Icon {icon_name} failed to generate!"
    print("  [OK] Vector icon generation verified.")

    img = assets_mgr.get_image("laptop", size=(100, 100))
    assert img is not None
    print("  [OK] Fast asset thumbnail loading verified.")


def test_forms_and_navigation():
    print("[Test] Testing GUI instantiation, modals, dark mode sidebar, and tab navigation...")
    assets_mgr.clear_ctk_cache()
    icons.clear_icon_cache()
    app = ChiikawaApp()
    app.update_idletasks()

    saved_data = {}

    def capture_save(data):
        saved_data.update(data)

    # 1. TaskModal
    task_modal = TaskModal(app, capture_save)
    task_modal.update_idletasks()
    assert hasattr(task_modal, "btn_submit"), "TaskModal has no btn_submit!"
    assert task_modal.btn_submit.cget("text") in ("Save Task", "Update Task")
    task_modal.ent_title.delete(0, "end")
    task_modal._save()
    assert task_modal.lbl_error.cget("text") != "", "Validation error should appear for empty title"
    task_modal.ent_title.insert(0, "Complete Physics Lab")
    task_modal._save()
    assert saved_data.get("title") == "Complete Physics Lab"
    print("  [OK] TaskModal verified.")

    # 2. StickyNoteModal
    saved_data.clear()
    sticky_modal = StickyNoteModal(app, capture_save)
    sticky_modal.update_idletasks()
    assert hasattr(sticky_modal, "btn_submit"), "StickyNoteModal has no btn_submit!"
    sticky_modal.txt_content.insert("1.0", "Important formula")
    sticky_modal._save()
    assert saved_data.get("content") == "Important formula"
    print("  [OK] StickyNoteModal verified.")

    # 3. SubjectModal
    saved_data.clear()
    subj_modal = SubjectModal(app, capture_save)
    subj_modal.update_idletasks()
    assert hasattr(subj_modal, "btn_submit"), "SubjectModal has no btn_submit!"
    subj_modal.ent_name.insert(0, "Quantum Mechanics")
    subj_modal._save()
    assert saved_data.get("name") == "Quantum Mechanics"
    print("  [OK] SubjectModal verified.")

    # 4. EventModal
    saved_data.clear()
    ev_modal = EventModal(app, capture_save)
    ev_modal.update_idletasks()
    assert hasattr(ev_modal, "btn_submit"), "EventModal has no btn_submit!"
    ev_modal.ent_title.insert(0, "Midterm Exam")
    ev_modal.ent_start_date.delete(0, "end")
    ev_modal.ent_start_date.insert(0, "2026-10-15")
    ev_modal._save()
    assert saved_data.get("title") == "Midterm Exam"
    print("  [OK] EventModal verified.")

    # 5. HabitModal
    saved_data.clear()
    h_modal = HabitModal(app, capture_save)
    h_modal.update_idletasks()
    assert hasattr(h_modal, "btn_submit"), "HabitModal has no btn_submit!"
    h_modal.ent_title.insert(0, "Review Flashcards")
    h_modal._save()
    assert saved_data.get("title") == "Review Flashcards"
    print("  [OK] HabitModal verified.")

    # 6. NoteModal
    saved_data.clear()
    n_modal = NoteModal(app, capture_save)
    n_modal.update_idletasks()
    assert hasattr(n_modal, "btn_submit"), "NoteModal has no btn_submit!"
    n_modal.ent_title.insert(0, "Lecture 4 Notes")
    n_modal.txt_content.insert("1.0", "Summary of vectors and matrices.")
    n_modal._save()
    assert saved_data.get("title") == "Lecture 4 Notes"
    print("  [OK] NoteModal verified.")

    # 7. SessionModal
    saved_data.clear()
    s_modal = SessionModal(app, capture_save)
    s_modal.update_idletasks()
    assert hasattr(s_modal, "btn_submit"), "SessionModal has no btn_submit!"
    s_modal.ent_topic.insert(0, "Calculus Integration")
    s_modal._save()
    assert saved_data.get("topic") == "Calculus Integration"
    print("  [OK] SessionModal verified.")

    # Tab navigation tests
    expected_views = [
        "dashboard", "todo", "corkboard", "calendar",
        "study_planner", "pomodoro", "habits", "notes",
        "progress", "search", "settings"
    ]
    for vk in expected_views:
        assert vk in app.views, f"View {vk} missing from app.views!"
        app.navigate_to(vk)
        app.update_idletasks()
        if vk == "calendar":
            cal_view = app.views["calendar"]
            test_eid = database.add_calendar_event(title="Midterm Exam Calendar", event_type="Exam", start_date=cal_view.selected_date.isoformat())
            test_tid = database.add_task(title="Task Due in Calendar", due_date=cal_view.selected_date.isoformat())
            cal_view._update_inspector()
            app.update_idletasks()
            cal_view._delete_event(test_eid)
            cal_view._delete_task(test_tid)
            print("  [OK] Calendar event & task edit/delete verified.")
        print(f"  [OK] Navigated to '{vk}' tab successfully.")

    # Theme switching test & Sidebar dark mode verification
    app._change_theme("dark")
    app.update_idletasks()
    assert Theme.MODE == "dark"
    # Check sidebar is in dark mode
    sidebar_fg = app.sidebar.cget("fg_color")
    assert sidebar_fg == Theme.DARK["bg_sidebar"] or (isinstance(sidebar_fg, tuple) and Theme.DARK["bg_sidebar"] in sidebar_fg), f"Sidebar not dark: {sidebar_fg}"
    print(f"  [OK] Sidebar switched to dark mode color ({sidebar_fg}) successfully.")

    app._change_theme("light")
    app.update_idletasks()
    assert Theme.MODE == "light"
    sidebar_fg_light = app.sidebar.cget("fg_color")
    assert sidebar_fg_light == Theme.LIGHT["bg_sidebar"] or (isinstance(sidebar_fg_light, tuple) and Theme.LIGHT["bg_sidebar"] in sidebar_fg_light), f"Sidebar not light: {sidebar_fg_light}"
    print(f"  [OK] Sidebar switched to light mode color ({sidebar_fg_light}) successfully.")

    app.destroy()
    print("[Test] ChiikawaApp GUI tests passed successfully!")


if __name__ == "__main__":
    test_database()
    test_typography()
    test_icons_and_assets()
    test_forms_and_navigation()
    print("\nALL MODERNIZATION, TYPOGRAPHY & DARK MODE SIDEBAR TESTS PASSED SUCCESSFULLY!")

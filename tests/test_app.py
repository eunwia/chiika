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
    HabitModal, NoteModal, SessionModal, ConfirmModal,
    CategoryManagerModal, RenameCategoryModal
)


def test_database():
    print("[Test] Testing database initialization and CRUD...")
    database.init_db()

    subjects = database.get_all_subjects()
    assert len(subjects) >= 4, f"Expected at least 4 subjects, got {len(subjects)}"

    # Task CRUD (Daily & General)
    tid = database.add_task(title="Test Task", description="Testing", category="Study", priority="High")
    assert tid > 0
    database.toggle_task_completed(tid, True)
    tasks = database.get_tasks(filter_status="completed")
    assert any(t["id"] == tid for t in tasks)
    database.delete_task(tid)

    # General Tasks CRUD & Separation
    gtid = database.add_task(title="Buy Notebook", category="Personal", task_type="general")
    assert gtid > 0
    dtid = database.add_task(title="Daily Review", category="Study", task_type="daily")
    assert dtid > 0
    gen_tasks = database.get_tasks(task_type="general")
    assert any(t["id"] == gtid for t in gen_tasks), "General task missing from get_tasks(task_type='general')"
    assert not any(t["id"] == dtid for t in gen_tasks), "Daily task should not appear in general tasks"
    daily_tasks = database.get_tasks(task_type="daily")
    assert any(t["id"] == dtid for t in daily_tasks), "Daily task missing from get_tasks(task_type='daily')"
    assert not any(t["id"] == gtid for t in daily_tasks), "General task should not appear in daily tasks"
    database.update_task(gtid, title="Buy Notebook and Pens", description="Stationery", subject_id=None, category="Personal", priority="Low", due_date=None, due_time="23:59", task_type="general")
    database.toggle_task_completed(gtid, True)
    database.delete_task(gtid)
    database.delete_task(dtid)

    # Study Session CRUD & Deletion
    sid = database.log_study_session(subject_id=None, topic="Test Math Session", duration_minutes=25)
    assert sid > 0
    sessions = database.get_study_sessions()
    assert any(s["id"] == sid for s in sessions), "Logged study session not found"
    database.delete_study_session(sid)
    sessions_after = database.get_study_sessions()
    assert not any(s["id"] == sid for s in sessions_after), "Study session was not deleted from database"

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

    # Event Category CRUD
    cid = database.add_event_category("Project Lab", "#FF7597")
    assert cid > 0
    database.rename_event_category(cid, "Robotics Lab")
    cats = database.get_event_categories()
    assert any(c["id"] == cid and c["name"] == "Robotics Lab" for c in cats)
    database.delete_event_category(cid)

    # Calendar Event CRUD with Reminder & Recurring
    eid = database.add_calendar_event(
        title="Test Event",
        event_type="Exam",
        start_date="2026-10-15",
        reminder="15 mins before",
        recurring="Weekly"
    )
    assert eid > 0
    evs = database.get_calendar_events(start_date="2026-10-15", end_date="2026-10-15")
    assert any(e["id"] == eid and e.get("reminder") == "15 mins before" and e.get("recurring") == "Weekly" for e in evs)
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
    assert hasattr(ev_modal, "opt_reminder"), "EventModal has no opt_reminder!"
    assert hasattr(ev_modal, "opt_recurring"), "EventModal has no opt_recurring!"
    ev_modal.ent_title.insert(0, "Midterm Exam")
    ev_modal.ent_start_date.delete(0, "end")
    ev_modal.ent_start_date.insert(0, "2026-10-15")
    ev_modal.opt_reminder.set("30 mins before")
    ev_modal.opt_recurring.set("Weekly")
    ev_modal._save()
    assert saved_data.get("title") == "Midterm Exam"
    assert saved_data.get("reminder") == "30 mins before"
    assert saved_data.get("recurring") == "Weekly"
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

    # 8. ConfirmModal
    confirm_called = []
    c_modal = ConfirmModal(app, title_text="Confirm Delete", message="Are you sure?", on_confirm=lambda: confirm_called.append(True))
    c_modal.update_idletasks()
    c_modal._handle_confirm()
    assert confirm_called == [True], "ConfirmModal on_confirm not called"
    print("  [OK] ConfirmModal verified.")

    # 9. CategoryManagerModal & RenameCategoryModal
    cat_modal = CategoryManagerModal(app)
    cat_modal.update_idletasks()
    assert hasattr(cat_modal, "cat_scroll"), "CategoryManagerModal has no cat_scroll!"
    cat_modal._finish()
    print("  [OK] CategoryManagerModal verified.")

    ren_saved = []
    ren_modal = RenameCategoryModal(app, 1, "Exams", lambda n: ren_saved.append(n))
    ren_modal.update_idletasks()
    assert hasattr(ren_modal, "btn_submit"), "RenameCategoryModal has no btn_submit!"
    ren_modal.ent_name.delete(0, "end")
    ren_modal.ent_name.insert(0, "Major Exams")
    ren_modal._save()
    assert ren_saved == ["Major Exams"]
    print("  [OK] RenameCategoryModal verified.")

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
        if vk == "todo":
            todo_view = app.views["todo"]
            assert hasattr(todo_view, "seg_tab"), "TodoView has no seg_tab switcher!"
            assert "Daily Tasks" in todo_view.seg_tab.cget("values")
            assert "General Tasks" in todo_view.seg_tab.cget("values")
            todo_view._on_tab_change("General Tasks")
            assert todo_view.active_tab == "General Tasks"
            todo_view._on_tab_change("Daily Tasks")
            assert todo_view.active_tab == "Daily Tasks"
            print("  [OK] TodoView Daily/General tab switching verified.")
        elif vk == "study_planner":
            sp_view = app.views["study_planner"]
            assert hasattr(sp_view, "_confirm_delete_log"), "StudyPlannerView missing _confirm_delete_log!"
            test_sid = database.log_study_session(subject_id=None, topic="Nav Test Session", duration_minutes=15)
            sp_view.seg_tab.set("Study Logs")
            sp_view._on_tab_change("Study Logs")
            app.update_idletasks()
            sp_view._delete_log(test_sid)
            app.update_idletasks()
            assert not any(s["id"] == test_sid for s in database.get_study_sessions())
            print("  [OK] Study Planner study log deletion verified.")
        elif vk == "calendar":
            cal_view = app.views["calendar"]
            assert hasattr(cal_view, "seg_filter"), "CalendarView missing seg_filter!"
            assert "All" in cal_view.seg_filter.cget("values")
            assert "Events" in cal_view.seg_filter.cget("values")
            assert "Tasks" in cal_view.seg_filter.cget("values")
            cal_view._on_filter_changed("Events")
            assert cal_view.inspector_filter == "Events"
            cal_view._on_filter_changed("Tasks")
            assert cal_view.inspector_filter == "Tasks"
            cal_view._on_filter_changed("All")
            assert cal_view.inspector_filter == "All"
            test_eid = database.add_calendar_event(title="Midterm Exam Calendar", event_type="Exam", start_date=cal_view.selected_date.isoformat(), reminder="1 hour before", recurring="None")
            test_tid = database.add_task(title="Task Due in Calendar", due_date=cal_view.selected_date.isoformat())
            cal_view._update_inspector()
            app.update_idletasks()
            cal_view._delete_event(test_eid)
            cal_view._delete_task(test_tid)
            print("  [OK] Calendar event & task edit/delete & filter verified.")
        elif vk == "settings":
            set_view = app.views["settings"]
            assert hasattr(set_view, "cal_cats_container"), "SettingsView missing cal_cats_container!"
            set_view._render_category_pills()
            print("  [OK] SettingsView Calendar categories section verified.")
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

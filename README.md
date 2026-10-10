# 🌸 Chiikawa Study Planner (チイカワ)

A modern, responsive, and cozy desktop study planner built with **Python**, **CustomTkinter**, **SQLite**, and **Pillow**.

---

## ✨ Highlights & Architecture Improvements

- ⚡ **Ultra-Fast Performance**: Pre-scaled 2x retina display thumbnails cached to disk (`static/cache/`) reduced asset load latency from 2.5s down to <5ms (a **500x speedup**).
- 🎨 **Modern Cozy Aesthetic**: Replaced harsh pink borders with clean, elevated white/slate card surfaces, hairline dividers (`#EAE4DC`), and tasteful pastel accents inspired by modern productivity tools (Notion, Things 3).
- 📐 **Vector-Style UI Icon Library (`icons.py`)**: Completely removed generic emojis from navigation and buttons. Uses antialiased supersampled vector-style monochrome and accent icons.
- 🛠️ **Fixed Add/Create Modals**: All creation and edit forms (`TaskModal`, `StickyNoteModal`, `SubjectModal`, `EventModal`, `HabitModal`, `NoteModal`, `SessionModal`) feature guaranteed, permanently pinned bottom action buttons (**Save Task**, **Create Note**, **Schedule Event**, etc.), working **Cancel** buttons, input validation, and `<Return>` shortcut bindings.
- 📱 **11 Integrated Features**:
  1. **Dashboard**: Greeting, 4 key metrics, schedule checklist, upcoming 7-day deadlines, quick-capture note.
  2. **Daily Tasks**: Full CRUD, category, priority, and date filters with instant check toggle.
  3. **Interactive Corkboard**: Real-time draggable sticky notes with persistent $(x, y)$ coordinates in SQLite.
  4. **Calendar**: Month, Week, and Day multi-views with date navigation and event scheduling.
  5. **Study Planner**: Course manager with total logged hours, exam countdowns, and study session history.
  6. **Focus Timer**: Pomodoro focus sprints (25m), short breaks (5m), and long breaks (15m) with automatic SQLite session logging.
  7. **Habit Tracker**: 7-day interactive checkboxes (Mon–Sun), streak counters, and weekly consistency metrics.
  8. **Notes**: Master-detail workspace with dedicated Create Note modal and inline editor.
  9. **Analytics & Progress**: Pure Canvas 7-day study activity bar chart, course time allocations, and achievement stats.
  10. **Universal Search**: Multi-attribute search across tasks, notes, and calendar events.
  11. **Settings**: Dual visual themes (**Cozy Day** 🌸 & **Cozy Night** 🌙), custom Pomodoro sprint durations, and database tools.

---

## 🚀 How to Launch the Application

In your terminal:
```bash
py app.py
```
Or run the batch script on Windows:
```bash
run.bat
```

To run the automated verification test suite:
```bash
py tests/test_app.py
```

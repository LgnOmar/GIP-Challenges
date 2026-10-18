# GIP-Challenges - GDG Algiers Dev Department

Welcome to the **GIP-Challenges** repository for the GDG Algiers Development Department!

This repository contains solutions to the internship/recruitment challenges, organized cleanly by level.

---

## Challenges Directory

| Level | Challenge | Tech Stack | Status | Details |
| :--- | :--- | :--- | :--- | :--- |
| **Level 1** | Lost & Found REST API | FastAPI + SQLite | Completed | [View Level 1 Details & Documentation](./Level%201/README.md) |
| **Level 2** | Interactive Scientific Calculator | HTML5, CSS3, Vanilla JS | Completed | [View Level 2 Details & Documentation](./Level%202/README.md) |
| **Level 3** | Upcoming Challenge | TBD | In Progress | Coming soon |

---

## Quick Start - Level 1 (Lost & Found API)

To run the Level 1 challenge:

```bash
cd "Level 1"
python -m uvicorn main:app --reload --port 8000
```

- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

To run tests for Level 1:

```bash
pytest "Level 1"
```

---

## Quick Start - Level 2 (Interactive Calculator)

To run the Level 2 challenge:

```bash
cd "Level 2"
# Simply open index.html in your browser, or start a local server:
python -m http.server 3000
```

Open `http://localhost:3000` in your web browser.

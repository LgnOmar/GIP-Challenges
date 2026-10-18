# Challenge 01: Easy - GDG Algiers

This directory contains the complete solutions for **Challenge 01: Easy** from the GDG Algiers Dev Department, structured by levels.

---

## Levels Overview

| Level | Task | Tech Stack | Status | Documentation |
| :--- | :--- | :--- | :--- | :--- |
| **Level 1** | Lost & Found REST API | FastAPI + SQLite | Completed | [Level 1 Documentation](./Level%201/README.md) |
| **Level 2** | Interactive Scientific Calculator | HTML5, CSS3, Vanilla JS | Completed | [Level 2 Documentation](./Level%202/README.md) |
| **Level 3** | Unique Binary String (Cantor's Diagonalization) | Python 3 | Completed | [Level 3 Documentation](./Level%203/README.md) |

---

## Quick Start

### Running Level 1 (Lost & Found API)
```bash
cd "Level 1"
python -m uvicorn main:app --reload --port 8000
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc UI: `http://127.0.0.1:8000/redoc`

To run automated tests for Level 1:
```bash
pytest "Level 1"
```

### Running Level 2 (Interactive Calculator)
```bash
cd "Level 2"
# Open index.html in any browser, or start a local server:
python -m http.server 3000
```
Navigate to `http://localhost:3000` in your web browser.

### Running Level 3 (Unique Binary String)
```bash
cd "Level 3"
python solution.py
```
To run automated tests for Level 3:
```bash
pytest "Level 3"
```

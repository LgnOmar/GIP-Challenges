# GIP-Challenges - GDG Algiers Dev Department

Welcome to the **GIP-Challenges** repository for the GDG Algiers Development Department!

This repository contains all solutions for the department challenges, organized by Challenge difficulty and Level.

---

## Repository Structure

```text
GIP-Challenges/
|-- Challenge-01-Easy/
|   |-- Level 1/            # Task 01: Lost & Found REST API (FastAPI + SQLite)
|   |-- Level 2/            # Task 02: Interactive Calculator (HTML/CSS/JS)
|   |-- Level 3/            # Task 03: Unique Binary String (Python 3)
|   `-- README.md
|-- Challenge-02-Medium/    # (Upcoming)
|-- Challenge-03-Hard/      # (Upcoming)
`-- README.md
```

---

## Challenges Directory

| Challenge | Difficulty | Levels Included | Status | Link |
| :--- | :--- | :--- | :--- | :--- |
| **Challenge 01** | Easy | Level 1, Level 2, Level 3 | Completed (3/3) | [Challenge 01 Details](./Challenge-01-Easy/README.md) |
| **Challenge 02** | Medium | Level 1, Level 2, Level 3 | Upcoming | Coming soon |
| **Challenge 03** | Hard | Level 1, Level 2, Level 3 | Upcoming | Coming soon |

---

## Quick Start - Challenge 01: Easy

### Level 1 (Lost & Found API)
```bash
cd "Challenge-01-Easy/Level 1"
python -m uvicorn main:app --reload --port 8000
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc UI: `http://127.0.0.1:8000/redoc`

Run automated tests:
```bash
pytest "Challenge-01-Easy/Level 1"
```

### Level 2 (Interactive Calculator)
```bash
cd "Challenge-01-Easy/Level 2"
python -m http.server 3000
```
Open `http://localhost:3000` in your web browser.

### Level 3 (Unique Binary String)
```bash
cd "Challenge-01-Easy/Level 3"
python solution.py
```

Run automated tests:
```bash
pytest "Challenge-01-Easy/Level 3"
```

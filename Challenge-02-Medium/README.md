# Challenge 02: Medium - GDG Algiers

This directory contains the complete solutions for **Challenge 02: Medium** from the GDG Algiers Dev Department, structured by levels.

---

## Levels Overview

| Level | Task | Tech Stack | Status | Documentation |
| :--- | :--- | :--- | :--- | :--- |
| **Level 1** | Client-Side Autocomplete Search | Vanilla HTML5, CSS3, JavaScript | Completed | [Level 1 Documentation](./Level%201/README.md) |
| **Level 2** | Secure Authentication API (Signup, Login, JWT) | FastAPI + SQLite + bcrypt + PyJWT | Completed | [Level 2 Documentation](./Level%202/README.md) |
| **Level 3** | First Missing Positive (Cyclic Placement) | Python 3 | Completed | [Level 3 Documentation](./Level%203/README.md) |

---

## Quick Start

### Running Level 1 (Autocomplete Search)
```bash
cd "Level 1"
# Open index.html in a browser or start a static server:
npx -y serve . -l 8080
```
Navigate to `http://localhost:8080` in your web browser.

### Running Level 2 (Secure Auth API)
```bash
cd "Level 2"
python -m uvicorn main:app --reload --port 8000
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Run automated tests:
```bash
pytest test_auth.py
```

### Running Level 3 (First Missing Positive)
```bash
cd "Level 3"
python solution.py
```
- Run automated tests:
```bash
pytest test_solution.py
```

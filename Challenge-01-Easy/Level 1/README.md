# Lost & Found API - GDG Algiers Challenge

A simple, lightweight, and clean REST API built with FastAPI and SQLite (zero external dependencies or database configuration required).

---

## Features

- Report Lost Items: Submit details of an item you lost (`POST /items/lost`).
- Report Found Items: Submit details of an item you found (`POST /items/found`).
- Search & Filter: Find items using keyword search (`title`, `description`, `location`), type (`lost`/`found`), `category`, `location`, and `status` (`reported`/`recovered`).
- View Item Details: Get the complete record of any item by its ID (`GET /items/{id}`).
- Update Own Reports: Edit title, description, location, or contact info. Secured by reporter email verification (`PUT /items/{id}`).
- Mark as Recovered: Mark an item as returned/found once resolved (`PATCH /items/{id}/recover`).
- Interactive Swagger Documentation: Built-in interactive testing UI at `http://127.0.0.1:8000/docs`.
- ReDoc UI: Alternative clean documentation at `http://127.0.0.1:8000/redoc`.

---

## Getting Started

### 1. Requirements

- Python 3.10+
- `fastapi` and `uvicorn` (already pre-installed)

### 2. Run the API Server

```bash
uvicorn main:app --reload --port 8000
```
Or simply:
```bash
python main.py
```

The server will start at:
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc UI: `http://127.0.0.1:8000/redoc`

---

## Running Automated Tests

Run the test suite with `pytest`:

```bash
pytest -v
```

All 9 test cases will verify reporting, searching, filtering, detail retrieval, authorization checks, and recovery marking.

---

## API Reference & Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/items/lost` | Report a lost item |
| `POST` | `/items/found` | Report a found item |
| `POST` | `/items` | Report an item (with `item_type: "lost"` or `"found"`) |
| `GET` | `/items` | Search & filter reported items |
| `GET` | `/items/{id}` | View full details of an item |
| `PUT` | `/items/{id}` | Update own report (requires `reporter_email`) |
| `PATCH` | `/items/{id}/recover` | Mark item as recovered (requires `reporter_email`) |
| `DELETE` | `/items/{id}` | Delete own report (requires `reporter_email`) |
| `GET` | `/stats` | Statistics summary |

---

## Quick Examples

### 1. Report a Lost Item
```bash
curl -X POST "http://127.0.0.1:8000/items/lost" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Claquetta Nike kahla w ferda wahda",
    "description": "Rani nsayi nefhem kifah rahtli ghir lferda lissra te3 claquetta fi amphi 4 mor cours te3 analyse.",
    "category": "Clothing",
    "location": "Amphi 4, USTHB",
    "date_occurred": "2026-10-17",
    "reporter_name": "Mourad Boukhemkhem",
    "reporter_email": "mourad.claquette@gmail.com",
    "reporter_phone": "0555112233"
  }'
```

### 2. Search & Filter Items
```bash
# Search by keyword
curl "http://127.0.0.1:8000/items?search=claquetta"

# Filter by lost items in a specific category
curl "http://127.0.0.1:8000/items?item_type=lost&category=Clothing"

# Filter active reports by location
curl "http://127.0.0.1:8000/items?location=Amphi&status=reported"
```

### 3. Update an Item Report
> Note: To prevent unauthorized tampering, updates require the original reporter's email.
```bash
curl -X PUT "http://127.0.0.1:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "reporter_email": "mourad.claquette@gmail.com",
    "location": "Amphi 4, USTHB (rang 3)",
    "reporter_phone": "0555998877"
  }'
```

### 4. Mark an Item as Recovered
```bash
curl -X PATCH "http://127.0.0.1:8000/items/1/recover" \
  -H "Content-Type: application/json" \
  -d '{
    "reporter_email": "mourad.claquette@gmail.com"
  }'
```

---

## Render Deployment Settings

- **Root Directory**: `Challenge-01-Easy/Level 1`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
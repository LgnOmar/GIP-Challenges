"""
Lost & Found API
Built with FastAPI & SQLite for simplicity, speed, and zero external configuration.

Endpoints:
- POST   /items/lost           : Report a lost item
- POST   /items/found          : Report a found item
- POST   /items                : Report any item (lost or found)
- GET    /items                : Search and filter reported items
- GET    /items/{item_id}      : View details of a specific item
- PUT    /items/{item_id}      : Update own report (verified by reporter_email)
- PATCH  /items/{item_id}/recover : Mark an item as recovered (verified by reporter_email)
- DELETE /items/{item_id}      : Delete own report (verified by reporter_email)
- GET    /stats                : Quick statistics overview
- GET    /redoc                : ReDoc UI with fixed standalone JS bundle
"""

import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from pydantic import BaseModel, Field

# Database configuration: self-contained inside Level 1 folder
DB_PATH = Path(__file__).resolve().parent / "lost_and_found.db"

# Sample dumb test data in authentic Algerian Darija
DARIJA_SEED_ITEMS = [
    {
        "title": "Claquetta Nike kahla w ferda wahda",
        "description": "Rani nsayi nefhem kifah rahtli ghir lferda lissra te3 claquetta fi amphi 4 mor cours te3 analyse. Li lqaha yarhem babakom yji yrejaha rani nemchi b ferda wahda kima lmajhoul.",
        "category": "Clothing",
        "item_type": "lost",
        "location": "Amphi 4, USTHB",
        "date_occurred": "2026-10-17",
        "date_reported": "2026-10-17T14:30:00",
        "status": "reported",
        "reporter_name": "Mourad Boukhemkhem",
        "reporter_email": "mourad.claquette@gmail.com",
        "reporter_phone": "0555112233",
    },
    {
        "title": "Carte Chifa + Carte d'etudiant + 200 DA maqdoussa",
        "description": "Twadherli sacoche sghira kahla fel resto U wla 9odam l'arret te3 l'Etusa. Fiha carte chifa te3 yemma w carte d'etudiant w 200 DA kount mkhabiha lel casse-croute garanti. Dourou ma bqali khawti.",
        "category": "Documents & Wallets",
        "item_type": "lost",
        "location": "Resto Universitaire / Arret Bus",
        "date_occurred": "2026-10-16",
        "date_reported": "2026-10-16T12:15:00",
        "status": "reported",
        "reporter_name": "Amine DZ",
        "reporter_email": "amine.chifa@gmail.com",
        "reporter_phone": "0661445566",
    },
    {
        "title": "Calculatrice Casio fx-991EX fiha sticker te3 CRB",
        "description": "Lqit calculatrice mhetta fog tabla numero 8 fel biblio te3 l'info mor maghreb. Fiha sticker te3 Chabab Belouizdad w mektoub men lor 'Rachid Info L3'. Li ta3ou ymedli l'email ta3ou ydiha.",
        "category": "Electronics",
        "item_type": "found",
        "location": "Bibliotheque centrale, 1er etage",
        "date_occurred": "2026-10-17",
        "date_reported": "2026-10-17T18:45:00",
        "status": "reported",
        "reporter_name": "Youcef Belkacem",
        "reporter_email": "youcef.crb@gmail.com",
        "reporter_phone": "0770998877",
    },
    {
        "title": "Trouseau te3 mfatel fih 4 mfateh w medallion te3 Eiffel Tower",
        "description": "Lqinahom fel cafeteria te3 l'annexe m3a sabah. Fihoum clef te3 dar w clef te3 moto w porte-cle Tour Eiffel sghir. Sahbhom l9ana w dja dahom elhamdoulilah.",
        "category": "Keys",
        "item_type": "found",
        "location": "Cafeteria l'Annexe",
        "date_occurred": "2026-10-15",
        "date_reported": "2026-10-15T09:20:00",
        "status": "recovered",
        "reporter_name": "Karim Cafet",
        "reporter_email": "karim.cafet@gmail.com",
        "reporter_phone": "0540123456",
    },
]


def get_db():
    """Dependency that yields an open SQLite connection with Row mapping."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def seed_initial_data(conn: sqlite3.Connection):
    """Seed sample Algerian Darija items if the table is empty."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            """
            INSERT INTO items (
                title, description, category, item_type, location,
                date_occurred, date_reported, status,
                reporter_name, reporter_email, reporter_phone
            ) VALUES (
                :title, :description, :category, :item_type, :location,
                :date_occurred, :date_reported, :status,
                :reporter_name, :reporter_email, :reporter_phone
            )
            """,
            DARIJA_SEED_ITEMS,
        )
        conn.commit()


def init_db():
    """Initializes the database schema and seeds initial data."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                item_type TEXT NOT NULL CHECK (item_type IN ('lost', 'found')),
                location TEXT NOT NULL,
                date_occurred TEXT,
                date_reported TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('reported', 'recovered')) DEFAULT 'reported',
                reporter_name TEXT NOT NULL,
                reporter_email TEXT NOT NULL,
                reporter_phone TEXT
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON items (item_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_status ON items (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items (category)")
        conn.commit()
        seed_initial_data(conn)


# Initialize database on load
init_db()

app = FastAPI(
    title="Lost & Found API",
    description=(
        "A lightweight, simple, and clean REST API to report lost and found items, "
        "search & filter reports, view item details, update reports, and mark items as recovered."
    ),
    version="1.0.0",
    redoc_url=None,  # Custom ReDoc route defined below to avoid import.meta JS bundle bug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- ReDoc Custom Route ---

@app.get("/redoc", include_in_schema=False)
def redoc_html():
    """
    Serves ReDoc UI using a stable standalone bundle that does not rely on
    unsupported 'import.meta' syntax outside ES modules.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.77/bundles/redoc.standalone.js",
    )


# --- Enums & Schemas ---

class ItemType(str, Enum):
    LOST = "lost"
    FOUND = "found"


class ItemStatus(str, Enum):
    REPORTED = "reported"
    RECOVERED = "recovered"


class ItemCreate(BaseModel):
    title: str = Field(..., example="Claquetta Nike kahla w ferda wahda", description="Short title of the item")
    description: str = Field(..., example="Rahtli lferda lissra fi amphi 4", description="Detailed description")
    category: str = Field(..., example="Clothing", description="Category (Clothing, Electronics, Documents & Wallets, Keys, Other)")
    location: str = Field(..., example="Amphi 4, USTHB", description="Where the item was lost or found")
    date_occurred: Optional[str] = Field(None, example="2026-10-17", description="Date when the item was lost/found")
    reporter_name: str = Field(..., example="Mourad Boukhemkhem", description="Full name of reporter")
    reporter_email: str = Field(..., example="mourad.claquette@gmail.com", description="Reporter email used to authorize updates")
    reporter_phone: Optional[str] = Field(None, example="0555112233", description="Contact phone number")


class ItemCreateWithType(ItemCreate):
    item_type: ItemType = Field(..., example=ItemType.LOST, description="'lost' or 'found'")


class ItemUpdate(BaseModel):
    reporter_email: str = Field(..., example="mourad.claquette@gmail.com", description="Must match the original reporter's email")
    title: Optional[str] = Field(None, example="Updated title")
    description: Optional[str] = Field(None, example="Updated description")
    category: Optional[str] = Field(None, example="Clothing")
    location: Optional[str] = Field(None, example="Amphi 4, rang 2")
    date_occurred: Optional[str] = Field(None, example="2026-10-17")
    reporter_phone: Optional[str] = Field(None, example="0555998877")


class RecoverRequest(BaseModel):
    reporter_email: str = Field(..., example="mourad.claquette@gmail.com", description="Must match the original reporter's email")


class ItemResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    item_type: str
    location: str
    date_occurred: Optional[str]
    date_reported: str
    status: str
    reporter_name: str
    reporter_email: str
    reporter_phone: Optional[str]


# Helper to convert SQLite row to dictionary
def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


# --- Endpoints ---

@app.get("/", tags=["Health & Info"])
def root():
    return {
        "message": "Welcome to the Lost & Found API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "report_lost": "POST /items/lost",
            "report_found": "POST /items/found",
            "search_and_filter": "GET /items",
            "view_item": "GET /items/{item_id}",
            "update_item": "PUT /items/{item_id}",
            "mark_recovered": "PATCH /items/{item_id}/recover",
            "statistics": "GET /stats",
        },
    }


@app.post(
    "/items/lost",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Report Items"],
    summary="Report a lost item",
)
def report_lost_item(item: ItemCreate, db: sqlite3.Connection = Depends(get_db)):
    """Report an item that you have lost."""
    return _create_item(item, ItemType.LOST, db)


@app.post(
    "/items/found",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Report Items"],
    summary="Report a found item",
)
def report_found_item(item: ItemCreate, db: sqlite3.Connection = Depends(get_db)):
    """Report an item that you have found."""
    return _create_item(item, ItemType.FOUND, db)


@app.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Report Items"],
    summary="Report an item (lost or found)",
)
def report_item(item: ItemCreateWithType, db: sqlite3.Connection = Depends(get_db)):
    """General endpoint to report either a lost or a found item."""
    return _create_item(item, item.item_type, db)


def _create_item(item: ItemCreate, item_type: ItemType, db: sqlite3.Connection) -> dict:
    now = datetime.utcnow().isoformat()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO items (
            title, description, category, item_type, location,
            date_occurred, date_reported, status,
            reporter_name, reporter_email, reporter_phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item.title.strip(),
            item.description.strip(),
            item.category.strip(),
            item_type.value,
            item.location.strip(),
            item.date_occurred.strip() if item.date_occurred else None,
            now,
            ItemStatus.REPORTED.value,
            item.reporter_name.strip(),
            item.reporter_email.strip().lower(),
            item.reporter_phone.strip() if item.reporter_phone else None,
        ),
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM items WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    return row_to_dict(row)


@app.get(
    "/items",
    response_model=List[ItemResponse],
    tags=["Search & Filter"],
    summary="Search and filter reported items",
)
def list_items(
    search: Optional[str] = None,
    item_type: Optional[ItemType] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[ItemStatus] = None,
    reporter_email: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Search and filter through all reported lost and found items.
    All filters can be combined.
    """
    conditions = []
    params = []

    if search:
        search_term = f"%{search.strip()}%"
        conditions.append("(title LIKE ? OR description LIKE ? OR location LIKE ?)")
        params.extend([search_term, search_term, search_term])

    if item_type:
        conditions.append("item_type = ?")
        params.append(item_type.value if hasattr(item_type, "value") else str(item_type))

    if category:
        conditions.append("category LIKE ?")
        params.append(f"%{category.strip()}%")

    if location:
        conditions.append("location LIKE ?")
        params.append(f"%{location.strip()}%")

    if status:
        conditions.append("status = ?")
        params.append(status.value if hasattr(status, "value") else str(status))

    if reporter_email:
        conditions.append("reporter_email = ?")
        params.append(reporter_email.strip().lower())

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"SELECT * FROM items {where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor = db.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [row_to_dict(row) for row in rows]


@app.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    tags=["Item Details"],
    summary="View details of a specific item",
)
def get_item_details(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Fetch complete details of a reported item by its ID."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found.",
        )
    return row_to_dict(row)


@app.put(
    "/items/{item_id}",
    response_model=ItemResponse,
    tags=["Manage Reports"],
    summary="Update your own report",
)
def update_item_report(
    item_id: int,
    update_data: ItemUpdate,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Update details of a previously reported item.
    Only the original reporter can update their report (verified by reporter_email).
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found.",
        )

    # Ownership check
    original_email = row["reporter_email"].strip().lower()
    provided_email = update_data.reporter_email.strip().lower()

    if provided_email != original_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only update your own reports. Provided email does not match the reporter email.",
        )

    # Build update statements only for supplied fields
    updates = []
    params = []

    if update_data.title is not None:
        updates.append("title = ?")
        params.append(update_data.title.strip())

    if update_data.description is not None:
        updates.append("description = ?")
        params.append(update_data.description.strip())

    if update_data.category is not None:
        updates.append("category = ?")
        params.append(update_data.category.strip())

    if update_data.location is not None:
        updates.append("location = ?")
        params.append(update_data.location.strip())

    if update_data.date_occurred is not None:
        updates.append("date_occurred = ?")
        params.append(update_data.date_occurred.strip())

    if update_data.reporter_phone is not None:
        updates.append("reporter_phone = ?")
        params.append(update_data.reporter_phone.strip())

    if not updates:
        return row_to_dict(row)

    params.append(item_id)
    update_query = f"UPDATE items SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(update_query, params)
    db.commit()

    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    updated_row = cursor.fetchone()
    return row_to_dict(updated_row)


@app.patch(
    "/items/{item_id}/recover",
    response_model=ItemResponse,
    tags=["Manage Reports"],
    summary="Mark an item as recovered",
)
def mark_item_as_recovered(
    item_id: int,
    req: RecoverRequest,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Mark a lost or found item as recovered.
    Requires reporter_email to verify ownership.
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found.",
        )

    # Ownership check
    original_email = row["reporter_email"].strip().lower()
    provided_email = req.reporter_email.strip().lower()

    if provided_email != original_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only mark your own reported items as recovered.",
        )

    cursor.execute(
        "UPDATE items SET status = ? WHERE id = ?",
        (ItemStatus.RECOVERED.value, item_id),
    )
    db.commit()

    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    updated_row = cursor.fetchone()
    return row_to_dict(updated_row)


@app.delete(
    "/items/{item_id}",
    tags=["Manage Reports"],
    summary="Delete own report",
)
def delete_item_report(
    item_id: int,
    reporter_email: str,
    db: sqlite3.Connection = Depends(get_db),
):
    """Delete a report if you are the original reporter."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found.",
        )

    if row["reporter_email"].strip().lower() != reporter_email.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only delete your own reports.",
        )

    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()
    return {"message": f"Item {item_id} successfully deleted."}


@app.get(
    "/stats",
    tags=["Statistics"],
    summary="Get summary statistics",
)
def get_statistics(db: sqlite3.Connection = Depends(get_db)):
    """Overview count of lost, found, active, and recovered items."""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM items")
    total_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE item_type = 'lost'")
    total_lost = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE item_type = 'found'")
    total_found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'recovered'")
    total_recovered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'reported'")
    total_active = cursor.fetchone()[0]

    return {
        "total_items": total_items,
        "total_lost": total_lost,
        "total_found": total_found,
        "active_reports": total_active,
        "recovered_items": total_recovered,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
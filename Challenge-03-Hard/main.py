"""
Flash Sale Backend API
GDG Algiers - Challenge 03: Hard

A minimal REST API for a flash sale with atomic inventory management,
transactional order creation, and database-enforced idempotency.

Stack: FastAPI + SQLite (WAL mode)
Concurrency strategy: BEGIN IMMEDIATE serializes writers; atomic conditional
UPDATE ensures stock never goes negative; idempotency key stored in same
transaction as order creation.
"""

import os
import json
import hashlib
import datetime
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# --- Configuration ---

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "flash_sale.db"))


# --- Database ---

def init_db(db_path: str = DB_PATH):
    """Create tables if they don't exist and enable WAL mode."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            price REAL NOT NULL,
            stock INTEGER NOT NULL CHECK (stock >= 0)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            total_price REAL NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS idempotency_keys (
            user_id TEXT NOT NULL,
            key TEXT NOT NULL,
            request_hash TEXT NOT NULL,
            response_body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (user_id, key)
        );
    """)
    conn.close()


def seed_db(db_path: str = DB_PATH):
    """Insert sample flash-sale products if the table is empty."""
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        products = [
            ("Wireless Earbuds Pro", "Noise-cancelling Bluetooth earbuds with 30h battery", 49.99, 50),
            ("Mechanical Keyboard RGB", "Hot-swappable switches, aluminum frame", 89.99, 30),
            ("4K Ultra Monitor 27-inch", "IPS panel, 144Hz, HDR600", 329.99, 15),
            ("Gaming Mouse Ultralight", "Wireless, 25K DPI sensor, 58g weight", 59.99, 100),
            ("USB-C Docking Station", "Triple display, 100W PD, 10Gbps data", 79.99, 75),
        ]
        conn.executemany(
            "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
            products,
        )
        conn.commit()
    conn.close()


@contextmanager
def get_db(db_path: str = DB_PATH):
    """Yield a connection with WAL mode, busy timeout, and manual transaction control."""
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conn
    finally:
        conn.close()


# --- Request / Response Schemas ---

class OrderRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Must be a positive integer")


# --- Application ---

app = FastAPI(title="Flash Sale API - Challenge 03: Hard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db(DB_PATH)
    seed_db(DB_PATH)


# --- Routes ---

@app.get("/products")
def list_products():
    """List all products and their available stock."""
    with get_db(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, name, description, price, stock FROM products"
        ).fetchall()
        return [dict(r) for r in rows]


@app.get("/products/{product_id}")
def get_product(product_id: int):
    """View a single product and its available stock."""
    with get_db(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, name, description, price, stock FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        return dict(row)


@app.post("/orders", status_code=201)
def create_order(
    body: OrderRequest,
    x_user_id: str = Header(...),
    idempotency_key: str = Header(...),
):
    """
    Place an order for one product.

    Requires X-User-Id and Idempotency-Key headers.
    Stock is decremented atomically inside a single transaction.
    Idempotency is enforced via database constraint.
    """
    request_hash = hashlib.sha256(
        json.dumps(
            {"product_id": body.product_id, "quantity": body.quantity},
            sort_keys=True,
        ).encode()
    ).hexdigest()

    with get_db(DB_PATH) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            # --- Idempotency check ---
            existing = conn.execute(
                "SELECT request_hash, response_body FROM idempotency_keys "
                "WHERE user_id = ? AND key = ?",
                (x_user_id, idempotency_key),
            ).fetchone()

            if existing:
                conn.execute("ROLLBACK")
                if existing["request_hash"] != request_hash:
                    raise HTTPException(
                        status_code=409,
                        detail="Idempotency key already used with different request data",
                    )
                return json.loads(existing["response_body"])

            # --- Validate product ---
            product = conn.execute(
                "SELECT id, price, stock FROM products WHERE id = ?",
                (body.product_id,),
            ).fetchone()

            if not product:
                conn.execute("ROLLBACK")
                raise HTTPException(status_code=404, detail="Product not found")

            # --- Atomic stock decrement ---
            cursor = conn.execute(
                "UPDATE products SET stock = stock - ? "
                "WHERE id = ? AND stock >= ?",
                (body.quantity, body.product_id, body.quantity),
            )

            if cursor.rowcount == 0:
                available = product["stock"]
                conn.execute("ROLLBACK")
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Insufficient stock. Available: {available}, "
                        f"requested: {body.quantity}"
                    ),
                )

            # --- Create order ---
            total_price = round(product["price"] * body.quantity, 2)
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()

            cursor = conn.execute(
                "INSERT INTO orders "
                "(user_id, product_id, quantity, total_price, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (x_user_id, body.product_id, body.quantity, total_price, now),
            )
            order_id = cursor.lastrowid

            response_data = {
                "id": order_id,
                "user_id": x_user_id,
                "product_id": body.product_id,
                "quantity": body.quantity,
                "total_price": total_price,
                "created_at": now,
            }

            # --- Store idempotency record ---
            conn.execute(
                "INSERT INTO idempotency_keys "
                "(user_id, key, request_hash, response_body, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    x_user_id,
                    idempotency_key,
                    request_hash,
                    json.dumps(response_data),
                    now,
                ),
            )

            conn.execute("COMMIT")
            return response_data

        except HTTPException:
            raise
        except Exception:
            conn.execute("ROLLBACK")
            raise


@app.get("/orders")
def list_orders(x_user_id: str = Header(...)):
    """List orders belonging to the authenticated user only."""
    with get_db(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, user_id, product_id, quantity, total_price, created_at "
            "FROM orders WHERE user_id = ? ORDER BY created_at DESC",
            (x_user_id,),
        ).fetchall()
        return [dict(r) for r in rows]

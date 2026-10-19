"""
Automated test suite for Flash Sale API.

Covers:
- Product listing and detail retrieval
- Order creation (success, invalid inputs, insufficient stock)
- Idempotency (same request, different request, different users)
- Concurrent purchases (stock safety under load)
- Concurrent idempotent retries (only one order created)
- Order isolation between users
"""

import os
import uuid
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from fastapi.testclient import TestClient

# --- Test database setup ---

TEST_DB = "test_flash_sale.db"
os.environ["DB_PATH"] = TEST_DB

from main import app, init_db, seed_db, get_db

client = TestClient(app)


def reset_db():
    """Drop and recreate the test database with fresh seed data."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    # Also remove WAL/SHM files
    for ext in ("-wal", "-shm"):
        p = TEST_DB + ext
        if os.path.exists(p):
            os.remove(p)
    init_db(TEST_DB)
    seed_db(TEST_DB)


@pytest.fixture(autouse=True)
def fresh_db():
    reset_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    for ext in ("-wal", "-shm"):
        p = TEST_DB + ext
        if os.path.exists(p):
            os.remove(p)


def uid():
    return str(uuid.uuid4())


def idem():
    return str(uuid.uuid4())


# ========================================================================
# Product endpoints
# ========================================================================

class TestProducts:
    def test_list_products(self):
        res = client.get("/products")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 5
        for p in data:
            assert "id" in p
            assert "name" in p
            assert "stock" in p
            assert p["stock"] >= 0

    def test_get_product(self):
        res = client.get("/products/1")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == 1
        assert data["stock"] > 0

    def test_get_product_not_found(self):
        res = client.get("/products/9999")
        assert res.status_code == 404


# ========================================================================
# Order creation - basic
# ========================================================================

class TestOrders:
    def test_create_order_success(self):
        user = uid()
        res = client.post(
            "/orders",
            json={"product_id": 1, "quantity": 2},
            headers={"X-User-Id": user, "Idempotency-Key": idem()},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["user_id"] == user
        assert data["product_id"] == 1
        assert data["quantity"] == 2
        assert data["total_price"] > 0
        assert "id" in data
        assert "created_at" in data

    def test_stock_decremented(self):
        before = client.get("/products/1").json()["stock"]
        client.post(
            "/orders",
            json={"product_id": 1, "quantity": 3},
            headers={"X-User-Id": uid(), "Idempotency-Key": idem()},
        )
        after = client.get("/products/1").json()["stock"]
        assert after == before - 3

    def test_invalid_quantity_zero(self):
        res = client.post(
            "/orders",
            json={"product_id": 1, "quantity": 0},
            headers={"X-User-Id": uid(), "Idempotency-Key": idem()},
        )
        assert res.status_code == 422

    def test_invalid_quantity_negative(self):
        res = client.post(
            "/orders",
            json={"product_id": 1, "quantity": -5},
            headers={"X-User-Id": uid(), "Idempotency-Key": idem()},
        )
        assert res.status_code == 422

    def test_nonexistent_product(self):
        res = client.post(
            "/orders",
            json={"product_id": 9999, "quantity": 1},
            headers={"X-User-Id": uid(), "Idempotency-Key": idem()},
        )
        assert res.status_code == 404

    def test_insufficient_stock(self):
        # Product 3 has 15 units
        res = client.post(
            "/orders",
            json={"product_id": 3, "quantity": 9999},
            headers={"X-User-Id": uid(), "Idempotency-Key": idem()},
        )
        assert res.status_code == 409
        assert "Insufficient stock" in res.json()["detail"]

    def test_missing_user_header(self):
        res = client.post(
            "/orders",
            json={"product_id": 1, "quantity": 1},
            headers={"Idempotency-Key": idem()},
        )
        assert res.status_code == 422

    def test_missing_idempotency_header(self):
        res = client.post(
            "/orders",
            json={"product_id": 1, "quantity": 1},
            headers={"X-User-Id": uid()},
        )
        assert res.status_code == 422


# ========================================================================
# Idempotency
# ========================================================================

class TestIdempotency:
    def test_same_key_same_request_returns_cached(self):
        user = uid()
        key = idem()
        body = {"product_id": 1, "quantity": 1}
        headers = {"X-User-Id": user, "Idempotency-Key": key}

        res1 = client.post("/orders", json=body, headers=headers)
        assert res1.status_code == 201

        res2 = client.post("/orders", json=body, headers=headers)
        assert res2.status_code == 201
        assert res2.json()["id"] == res1.json()["id"]

        # Stock should only be decremented once
        stock_before = 50  # product 1 seed stock
        stock_after = client.get("/products/1").json()["stock"]
        assert stock_after == stock_before - 1

    def test_same_key_different_request_409(self):
        user = uid()
        key = idem()
        headers = {"X-User-Id": user, "Idempotency-Key": key}

        res1 = client.post(
            "/orders", json={"product_id": 1, "quantity": 1}, headers=headers
        )
        assert res1.status_code == 201

        res2 = client.post(
            "/orders", json={"product_id": 1, "quantity": 2}, headers=headers
        )
        assert res2.status_code == 409
        assert "different request data" in res2.json()["detail"].lower()

    def test_same_key_different_users_independent(self):
        key = idem()
        user_a = uid()
        user_b = uid()
        body = {"product_id": 1, "quantity": 1}

        res_a = client.post(
            "/orders",
            json=body,
            headers={"X-User-Id": user_a, "Idempotency-Key": key},
        )
        res_b = client.post(
            "/orders",
            json=body,
            headers={"X-User-Id": user_b, "Idempotency-Key": key},
        )
        assert res_a.status_code == 201
        assert res_b.status_code == 201
        assert res_a.json()["id"] != res_b.json()["id"]


# ========================================================================
# Order isolation
# ========================================================================

class TestOrderIsolation:
    def test_users_see_only_own_orders(self):
        user_a = uid()
        user_b = uid()

        client.post(
            "/orders",
            json={"product_id": 1, "quantity": 1},
            headers={"X-User-Id": user_a, "Idempotency-Key": idem()},
        )
        client.post(
            "/orders",
            json={"product_id": 2, "quantity": 1},
            headers={"X-User-Id": user_b, "Idempotency-Key": idem()},
        )

        orders_a = client.get("/orders", headers={"X-User-Id": user_a}).json()
        orders_b = client.get("/orders", headers={"X-User-Id": user_b}).json()

        assert len(orders_a) == 1
        assert len(orders_b) == 1
        assert orders_a[0]["product_id"] == 1
        assert orders_b[0]["product_id"] == 2

    def test_no_orders_returns_empty(self):
        res = client.get("/orders", headers={"X-User-Id": uid()})
        assert res.status_code == 200
        assert res.json() == []


# ========================================================================
# Concurrency tests
# ========================================================================

class TestConcurrency:
    def test_concurrent_purchases_never_oversell(self):
        """
        Product 3 (4K Monitor) has stock=15.
        Send 30 concurrent requests each for quantity=1.
        Exactly 15 should succeed; final stock must be 0.
        """
        product_id = 3
        initial_stock = client.get(f"/products/{product_id}").json()["stock"]
        assert initial_stock == 15

        results = []

        def place_order():
            return client.post(
                "/orders",
                json={"product_id": product_id, "quantity": 1},
                headers={"X-User-Id": uid(), "Idempotency-Key": idem()},
            )

        with ThreadPoolExecutor(max_workers=15) as pool:
            futures = [pool.submit(place_order) for _ in range(30)]
            for f in as_completed(futures):
                results.append(f.result())

        successes = [r for r in results if r.status_code == 201]
        failures = [r for r in results if r.status_code == 409]

        assert len(successes) == initial_stock, (
            f"Expected {initial_stock} successes, got {len(successes)}"
        )
        assert len(failures) == 30 - initial_stock

        final_stock = client.get(f"/products/{product_id}").json()["stock"]
        assert final_stock == 0, f"Stock should be 0, got {final_stock}"

    def test_concurrent_idempotent_retries(self):
        """
        Send 10 concurrent requests with the same idempotency key.
        Only 1 order should be created; all should return the same order ID.
        """
        product_id = 4  # Gaming Mouse, stock=100
        user = uid()
        key = idem()
        body = {"product_id": product_id, "quantity": 1}
        headers = {"X-User-Id": user, "Idempotency-Key": key}

        stock_before = client.get(f"/products/{product_id}").json()["stock"]

        results = []

        def retry():
            return client.post("/orders", json=body, headers=headers)

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(retry) for _ in range(10)]
            for f in as_completed(futures):
                results.append(f.result())

        # All should return 201
        assert all(r.status_code == 201 for r in results), (
            f"Status codes: {[r.status_code for r in results]}"
        )

        # All should return the same order ID
        order_ids = {r.json()["id"] for r in results}
        assert len(order_ids) == 1, f"Expected 1 unique order, got {order_ids}"

        # Stock should have decreased by exactly 1
        stock_after = client.get(f"/products/{product_id}").json()["stock"]
        assert stock_after == stock_before - 1

        # Only 1 order in the database for this user
        orders = client.get("/orders", headers={"X-User-Id": user}).json()
        assert len(orders) == 1

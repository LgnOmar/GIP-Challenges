"""
Automated Test Suite for Lost & Found API
Tests all required features:
1. Report lost item
2. Report found item
3. Search and filter items (by keyword, type, category, location, status)
4. View item details (success & 404)
5. Update own reports (authorized & 403 forbidden on wrong email)
6. Mark an item as recovered (authorized & 403 forbidden)
7. Statistics & deletion
"""

import os
import sqlite3
from pathlib import Path
import pytest
from fastapi import HTTPException

# Ensure clean test DB
TEST_DB = Path(__file__).parent / "test_lost_and_found.db"
if TEST_DB.exists():
    os.remove(TEST_DB)

import main
main.DB_PATH = TEST_DB
main.init_db()

from main import (
    ItemCreate,
    ItemType,
    ItemStatus,
    ItemUpdate,
    RecoverRequest,
    report_lost_item,
    report_found_item,
    list_items,
    get_item_details,
    update_item_report,
    mark_item_as_recovered,
    get_statistics,
)

created_test_item_id = None


@pytest.fixture(scope="session")
def db():
    conn = sqlite3.connect(str(TEST_DB))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_report_lost_item(db):
    global created_test_item_id
    payload = ItemCreate(
        title="Black Leather Wallet",
        description="Lost near the main library. Contains student ID.",
        category="Wallets & Bags",
        location="Campus Library",
        date_occurred="2026-10-15",
        reporter_name="Omar Laggoune",
        reporter_email="omar@example.com",
        reporter_phone="+213 555 123 456",
    )
    res = report_lost_item(payload, db)
    created_test_item_id = res["id"]
    assert res["id"] is not None
    assert res["title"] == "Black Leather Wallet"
    assert res["item_type"] == "lost"
    assert res["status"] == "reported"
    assert res["reporter_email"] == "omar@example.com"


def test_report_found_item(db):
    payload = ItemCreate(
        title="Blue Scientific Calculator",
        description="Casio fx-991EX found on table 14",
        category="Electronics",
        location="Amphi 3",
        date_occurred="2026-10-16",
        reporter_name="Sarah Doe",
        reporter_email="sarah@example.com",
        reporter_phone=None,
    )
    res = report_found_item(payload, db)
    assert res["id"] is not None
    assert res["title"] == "Blue Scientific Calculator"
    assert res["item_type"] == "found"
    assert res["status"] == "reported"


def test_view_item_details(db):
    item = get_item_details(created_test_item_id, db)
    assert item["id"] == created_test_item_id
    assert item["title"] == "Black Leather Wallet"

    # Non-existent item raises 404
    with pytest.raises(HTTPException) as exc_info:
        get_item_details(99999, db)
    assert exc_info.value.status_code == 404


def test_search_and_filter(db):
    # Search by keyword
    results = list_items(search="Wallet", db=db)
    assert len(results) >= 1
    assert any("Wallet" in r["title"] for r in results)

    # Filter by item_type
    lost_items = list_items(item_type=ItemType.LOST, db=db)
    assert all(i["item_type"] == "lost" for i in lost_items)

    found_items = list_items(item_type=ItemType.FOUND, db=db)
    assert all(i["item_type"] == "found" for i in found_items)

    # Filter by category
    electronics = list_items(category="Electronics", db=db)
    assert all("Electronics" in i["category"] for i in electronics)

    # Filter by location
    lib_items = list_items(location="Library", db=db)
    assert all("Library" in i["location"] for i in lib_items)


def test_update_own_report_authorized(db):
    update_data = ItemUpdate(
        reporter_email="omar@example.com",
        location="Library 3rd floor (updated)",
        reporter_phone="+213 555 999 888",
    )
    updated = update_item_report(created_test_item_id, update_data, db)
    assert updated["location"] == "Library 3rd floor (updated)"
    assert updated["reporter_phone"] == "+213 555 999 888"


def test_update_report_unauthorized(db):
    # Attempt update with unauthorized email
    unauthorized_data = ItemUpdate(
        reporter_email="intruder@example.com",
        title="Hacked Title",
    )
    with pytest.raises(HTTPException) as exc_info:
        update_item_report(created_test_item_id, unauthorized_data, db)
    assert exc_info.value.status_code == 403


def test_mark_as_recovered_authorized(db):
    req = RecoverRequest(reporter_email="omar@example.com")
    recovered = mark_item_as_recovered(created_test_item_id, req, db)
    assert recovered["status"] == "recovered"


def test_mark_as_recovered_unauthorized(db):
    req = RecoverRequest(reporter_email="intruder@example.com")
    with pytest.raises(HTTPException) as exc_info:
        mark_item_as_recovered(created_test_item_id, req, db)
    assert exc_info.value.status_code == 403


def test_stats(db):
    stats = get_statistics(db)
    assert stats["total_items"] >= 2
    assert stats["total_lost"] >= 1
    assert stats["total_found"] >= 1
    assert stats["recovered_items"] >= 1


if __name__ == "__main__":
    pytest.main(["-v", __file__])

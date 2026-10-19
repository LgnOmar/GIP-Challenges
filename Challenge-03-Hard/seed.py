"""Standalone seed script. Initializes and populates the flash_sale database."""

from main import init_db, seed_db, DB_PATH

if __name__ == "__main__":
    init_db(DB_PATH)
    seed_db(DB_PATH)
    print(f"Database '{DB_PATH}' initialized and seeded with sample products.")

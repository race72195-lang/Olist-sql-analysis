"""Loads the Olist CSV files from data/ into a local SQLite database (olist.db)."""

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "olist.db"

# table name in SQL -> CSV file name
TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_orders_id ON orders(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_orders_customer ON orders(customer_id)",
    "CREATE INDEX IF NOT EXISTS ix_items_order ON order_items(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_items_product ON order_items(product_id)",
    "CREATE INDEX IF NOT EXISTS ix_items_seller ON order_items(seller_id)",
    "CREATE INDEX IF NOT EXISTS ix_payments_order ON payments(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_reviews_order ON reviews(order_id)",
    "CREATE INDEX IF NOT EXISTS ix_customers_id ON customers(customer_id)",
    "CREATE INDEX IF NOT EXISTS ix_products_id ON products(product_id)",
]


def build_db(force=False):
    """Create olist.db from the CSV files (skipped if it already exists)."""
    if sqlite3.sqlite_version_info < (3, 25):
        raise SystemExit("Your SQLite is too old for window functions (need 3.25+).")
    if DB_PATH.exists() and not force:
        return
    missing = [f for f in TABLES.values() if not (DATA_DIR / f).exists()]
    if missing:
        raise SystemExit(
            "Missing files in data/: " + ", ".join(missing)
            + "\nRun  python get_data.py  first (or put the Olist CSV files into data/)."
        )
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as conn:
        for table, file_name in TABLES.items():
            df = pd.read_csv(DATA_DIR / file_name)
            df.to_sql(table, conn, index=False)
            print(f"loaded {table:<22} {len(df):>9,} rows")
        for statement in INDEXES:
            conn.execute(statement)
    print("Database ready:", DB_PATH)


if __name__ == "__main__":
    build_db(force=True)

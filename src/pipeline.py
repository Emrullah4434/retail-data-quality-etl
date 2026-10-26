"""Validate CSV, normalize rows and load SQLite warehouse tables. stdlib only."""
from pathlib import Path
import csv
import sqlite3
from datetime import date

BASE = Path(__file__).resolve().parents[1]
SRC = BASE / "data" / "retail_transactions.csv"
DB = BASE / "outputs" / "retail_warehouse.sqlite"
DB.parent.mkdir(exist_ok=True)

required = {"transaction_id", "order_id", "transaction_date", "store_format", "region", "category", "units", "unit_price", "discount_pct", "returned"}
rows=[]; seen=set()
with SRC.open(newline="", encoding="utf-8") as f:
    reader=csv.DictReader(f)
    if not required.issubset(reader.fieldnames or []):
        raise ValueError(f"Missing columns: {required-set(reader.fieldnames or [])}")
    for i, raw in enumerate(reader, start=2):
        tid=raw['transaction_id']
        if not tid or tid in seen: raise ValueError(f"Duplicate or empty transaction_id at CSV line {i}")
        seen.add(tid)
        try:
            date.fromisoformat(raw['transaction_date'])
            units=int(raw['units']); price=float(raw['unit_price']); discount=float(raw['discount_pct']); returned=int(raw['returned'])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid numeric/date field at line {i}: {exc}") from exc
        if units<=0 or price<0 or not 0<=discount<=1 or returned not in (0,1):
            raise ValueError(f"Out-of-range value at CSV line {i}")
        if not all(raw[k].strip() for k in ('order_id','store_format','region','category')):
            raise ValueError(f"Missing dimension at CSV line {i}")
        net=round(units*price*(1-discount)*(1-returned), 2)
        rows.append((tid,raw['order_id'],raw['transaction_date'],raw['store_format'],raw['region'],raw['category'],units,price,discount,returned,net))

with sqlite3.connect(DB) as conn:
    conn.executescript("""CREATE TABLE IF NOT EXISTS retail_fact (
      transaction_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, transaction_date TEXT NOT NULL,
      store_format TEXT NOT NULL, region TEXT NOT NULL, category TEXT NOT NULL,
      units INTEGER NOT NULL, unit_price REAL NOT NULL, discount_pct REAL NOT NULL,
      returned INTEGER NOT NULL, net_sales REAL NOT NULL);
      CREATE INDEX IF NOT EXISTS idx_retail_date ON retail_fact(transaction_date);
      CREATE INDEX IF NOT EXISTS idx_retail_category ON retail_fact(category);
    """)
    conn.execute('DELETE FROM retail_fact')
    conn.executemany('INSERT INTO retail_fact VALUES (?,?,?,?,?,?,?,?,?,?,?)',rows)
    count, net=conn.execute('SELECT COUNT(*), ROUND(SUM(net_sales),2) FROM retail_fact').fetchone()
    assert count==len(rows)
print(f"Rows loaded: {count}; Net sales: {net:.2f}; DB: {DB}")

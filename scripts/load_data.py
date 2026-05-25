"""
IPL Data Loader
===============
Reads raw CSVs and stores them as tables in a SQLite database.

    data/raw/matches.csv    → matches table in data/ipl.db
    data/raw/deliveries.csv → deliveries table in data/ipl.db

Run from project root:
    python scripts/load_data.py
"""

import pandas as pd
import sqlite3
def load_raw():
    """Load both CSVs and return as DataFrames."""
    matches    = pd.read_csv("data/raw/matches.csv")
    deliveries = pd.read_csv("data/raw/deliveries.csv")
    print(f"Matches:    {matches.shape}")
    print(f"Deliveries: {deliveries.shape}")
    return matches, deliveries
def save_to_sqlite(matches, deliveries, db_path="data/ipl.db"):
    """
    Store DataFrames in SQLite for SQL-based analysis.
    if_exists='replace' drops and recreates the table — 
    use 'append' to add rows to existing table.
    """
    conn = sqlite3.connect(db_path)
    matches.to_sql("matches", conn, if_exists="replace", index=False)
    deliveries.to_sql("deliveries", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved to {db_path}")
matches, deliveries = load_raw()
save_to_sqlite(matches, deliveries)
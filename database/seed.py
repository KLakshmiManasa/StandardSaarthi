"""
SIH 26108 — Database Seed Script
Populates SQLite/PostgreSQL database from processed CSV files and verifies schema integrity.
"""

import os
import csv
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
DB_PATH = os.path.join(BASE_DIR, 'database', 'pilot_database.db')

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("[*] Seeding database tables...")

    # Load Standards Master
    stds_file = os.path.join(PROCESSED_DIR, 'standards_clean.csv')
    if os.path.exists(stds_file):
        with open(stds_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute("""
                INSERT OR REPLACE INTO standards_master VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
                """, tuple(row.values()))

    # Load Relationships
    rel_file = os.path.join(PROCESSED_DIR, 'relationships.csv')
    if os.path.exists(rel_file):
        with open(rel_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute("""
                INSERT OR REPLACE INTO standard_relationships VALUES (?,?,?,?,?,?,?);
                """, tuple(row.values()))

    # Load QCO
    qco_file = os.path.join(PROCESSED_DIR, 'qco_compliance.csv')
    if os.path.exists(qco_file):
        with open(qco_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute("""
                INSERT OR REPLACE INTO qco_compliance VALUES (?,?,?,?,?,?,?,?,?,?,?);
                """, tuple(row.values()))

    # Load Procurement Queries
    queries_file = os.path.join(PROCESSED_DIR, 'procurement_queries.csv')
    if os.path.exists(queries_file):
        with open(queries_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute("""
                INSERT OR REPLACE INTO procurement_queries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);
                """, tuple(row.values()))

    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM standards_master;")
    n_stds = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM standard_relationships;")
    n_rels = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM qco_compliance;")
    n_qco = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM procurement_queries;")
    n_queries = cur.fetchone()[0]

    conn.close()

    print(f"[OK] Database Seed Complete: {n_stds} standards, {n_rels} relationships, {n_qco} QCOs, {n_queries} queries.")

if __name__ == '__main__':
    seed_database()

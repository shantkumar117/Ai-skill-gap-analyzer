#!/usr/bin/env python3
"""Migrate AI Skill Gap Analyzer SQLite DB -> PostgreSQL (Supabase/Neon)."""
import sqlite3, os
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    raise SystemExit("pip install psycopg2-binary")

PG_URL = os.getenv("DATABASE_URL")
if not PG_URL:
    raise SystemExit("Set DATABASE_URL env to Postgres connection string")

DB = "database/skill_gap.db"

def get_sqlite():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_pg():
    return psycopg2.connect(PG_URL)

def migrate_table(pg, table, cursor_sqlite):
    # Get columns from SQLite
    cursor_sqlite.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cursor_sqlite.fetchall()]
    # Fetch all rows
    cursor_sqlite.execute(f"SELECT * FROM {table}")
    rows = cursor_sqlite.fetchall()
    if not rows:
        print(f"{table}: 0 rows")
        return
    # Build insert with placeholders
    placeholders = ",".join(["%s"] * len(cols))
    col_str = ",".join(cols)
    with pg.cursor() as cur:
        # Try insert; skip duplicates via ON CONFLICT or truncate+load
        cur.execute(f"TRUNCATE {table} RESTART IDENTITY CASCADE")
        for row in rows:
            cur.execute(f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})", tuple(row))
    pg.commit()
    print(f"{table}: {len(rows)} migrated")

pg = get_pg()
sqlite = get_sqlite()
cur = sqlite.cursor()

tables = ["AuthUsers","PasswordReset","Analysis","Skills","RoleSkills","UserSkills","Users"]
for t in tables:
    try:
        migrate_table(pg, t, cur)
    except Exception as e:
        print(f"{t}: ERROR {e}")

sqlite.close(); pg.close()
print("Migration complete. Verify with SELECT * FROM AuthUsers LIMIT 1;")

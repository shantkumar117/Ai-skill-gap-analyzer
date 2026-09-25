import os
import json
import re
import sqlite3
try:
    import psycopg2
    import psycopg2.extras
    HAS_PG = True
except Exception:
    HAS_PG = False
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "skill_gap.db"


def _integrity_errors():
    errors = [sqlite3.IntegrityError]
    if HAS_PG:
        errors.append(psycopg2.IntegrityError)
    return tuple(errors)


def _adapt_sql_for_pg(query):
    """Translate SQLite SQL so it runs on Postgres."""
    q = query
    if q.strip().upper().startswith("INSERT OR IGNORE"):
        q = re.sub(r"(?i)^INSERT OR IGNORE", "INSERT", q, count=1)
        q = q.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    q = q.replace("datetime('now', '+' || ? || ' hours')", "NOW() + make_interval(hours => %s)")
    q = q.replace("datetime('now', '-30 days')", "NOW() - INTERVAL '30 days'")
    q = q.replace("datetime('now')", "NOW()")
    q = q.replace("COALESCE(strftime('%Y-%m-%d %H:%M:%S', a.created_at), datetime('now'))", "COALESCE(to_char(a.created_at, 'YYYY-MM-DD HH24:MI:SS'), to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))")
    q = q.replace("julianday('now')", "(EXTRACT(EPOCH FROM NOW())/86400.0)")
    q = q.replace("julianday(a.created_at)", "(EXTRACT(EPOCH FROM a.created_at)/86400.0)")
    q = q.replace("MAX(0,", "GREATEST(0,")
    q = q.replace("?", "%s")
    return q


class PGConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, query, params=()):
        cur = self._conn.cursor()
        cur.execute(_adapt_sql_for_pg(query), params or ())
        cur.rowcount = cur.rowcount or -1
        return cur

    def executescript(self, script):
        # Schema already created in Supabase; skip SQLite DDL on Postgres.
        return None

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def wrap_connection(conn):
    if hasattr(conn, "cursor") and not hasattr(conn, "execute"):
        return PGConnectionWrapper(conn)
    return conn

ROLE_SKILLS = {
    "Frontend Developer": [
        ("HTML", "High"), ("CSS", "High"), ("JavaScript", "High"),
        ("Git", "Medium"), ("Responsive Design", "High"), ("React", "Medium"),
    ],
    "Backend Developer": [
        ("Python", "High"), ("SQL", "High"), ("Git", "Medium"),
        ("REST API", "High"), ("Django", "High"), ("Docker", "Medium"),
    ],
    "Full Stack Developer": [
        ("HTML", "High"), ("CSS", "High"), ("JavaScript", "High"),
        ("React", "Medium"), ("Python", "High"), ("SQL", "High"),
        ("REST API", "High"), ("Git", "Medium"),
    ],
    "AI / ML Engineer": [
        ("Python", "High"), ("PyTorch / TensorFlow", "High"), ("Machine Learning", "High"),
        ("Deep Learning", "High"), ("Data Structures", "Medium"), ("SQL", "Medium"),
        ("Git", "Medium"), ("Docker", "Medium"),
    ],
    "DevOps / Cloud Engineer": [
        ("Linux", "High"), ("Docker", "High"), ("Kubernetes", "High"),
        ("CI/CD", "High"), ("AWS / Cloud", "High"), ("Git", "High"),
        ("Terraform / IaC", "Medium"), ("Python", "Medium"),
    ],
    "Mobile Developer (Flutter / React Native)": [
        ("Dart / Flutter", "High"), ("JavaScript / React Native", "High"), ("REST API", "High"),
        ("Git", "Medium"), ("State Management", "High"), ("UI/UX Design", "Medium"),
    ],
    "Cybersecurity Analyst": [
        ("Network Security", "High"), ("Linux", "High"), ("Python", "Medium"),
        ("Vulnerability Assessment", "High"), ("SIEM & Log Analysis", "High"), ("Cryptography", "Medium"),
    ],
    "Data Analyst": [
        ("Python", "High"), ("SQL", "High"), ("Excel", "High"),
        ("Statistics", "High"), ("Power BI", "Medium"), ("Data Visualization", "High"),
    ],
    "Data Scientist": [
        ("Python", "High"), ("SQL", "Medium"), ("Statistics", "High"),
        ("Machine Learning", "High"), ("Pandas", "High"), ("Data Visualization", "Medium"),
    ],
    "Python Developer": [
        ("Python", "High"), ("SQL", "Medium"), ("Git", "Medium"),
        ("Object-Oriented Programming", "High"), ("Django", "High"), ("Testing", "Medium"),
    ],
    "Java Developer": [
        ("Java", "High"), ("SQL", "High"), ("Git", "Medium"),
        ("Object-Oriented Programming", "High"), ("Spring Boot", "High"), ("Testing", "Medium"),
    ],
    "Software Engineer": [
        ("Python", "Medium"), ("Java", "Medium"), ("Data Structures", "High"),
        ("Algorithms", "High"), ("Git", "High"), ("SQL", "Medium"),
    ],
}


def get_connection():
    DATABASE_DIR.mkdir(exist_ok=True)
    if HAS_PG and os.getenv("DATABASE_URL"):
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return wrap_connection(conn)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10.0, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS AuthUsers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE
        );
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            target_role TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS RoleSkills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            importance TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS PasswordReset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES AuthUsers (id)
        );
        CREATE TABLE IF NOT EXISTS UserSkills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users (id)
        );
        CREATE TABLE IF NOT EXISTS Analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_percentage REAL NOT NULL,
            missing_skills TEXT NOT NULL,
            recommendations TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            result_json TEXT,
            keep_forever INTEGER DEFAULT 0,
            target_role TEXT,
            FOREIGN KEY (user_id) REFERENCES Users (id)
        );
        """
    )
    for role, skills in ROLE_SKILLS.items():
        for skill_name, importance in skills:
            connection.execute("INSERT OR IGNORE INTO Skills (skill_name) VALUES (?)", (skill_name,))
            exists = connection.execute(
                "SELECT 1 FROM RoleSkills WHERE role = ? AND skill_name = ?",
                (role, skill_name),
            ).fetchone()
            if not exists:
                connection.execute(
                    "INSERT INTO RoleSkills (role, skill_name, importance) VALUES (?, ?, ?)",
                    (role, skill_name, importance),
                )
    connection.commit()
    connection.close()


def create_user(username, password_hash, email=None):
    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO AuthUsers (username, password_hash, email) VALUES (%s, %s, %s)",
            (username, password_hash, email),
        )
        user_id = connection.execute("SELECT lastval()").fetchone()[0]
        connection.execute(
            "INSERT OR IGNORE INTO Users (id, name, experience_level, target_role) VALUES (%s, %s, %s, %s)",
            (user_id, username, "Beginner", "Software Engineer"),
        )
        connection.commit()
        return True
    except _integrity_errors():
        connection.rollback()
        return False
    finally:
        connection.close()


def get_user_by_username(username):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM AuthUsers WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def get_user_by_email(email):
    connection = get_connection()
    try:
        row = connection.execute("SELECT * FROM AuthUsers WHERE email = ?", (email,)).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def save_analysis(user_id, name, experience_level, target_role, current_skills, match_percentage, missing_skills, recommendations):
    connection = get_connection()
    try:
        existing = connection.execute("SELECT id, username FROM AuthUsers WHERE id = ?", (user_id,)).fetchone()
        if existing:
            # Only overwrite the login username if it hasn't been changed to a different display name already; avoid UNIQUE crash
            if name and name != existing["username"]:
                try:
                    connection.execute("UPDATE AuthUsers SET username = ? WHERE id = ?", (name, user_id))
                except _integrity_errors():
                    connection.rollback()
        connection.execute(
            "INSERT OR IGNORE INTO Analysis (user_id, match_percentage, missing_skills, recommendations, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, match_percentage, json.dumps(missing_skills), json.dumps(recommendations)),
        )
        for skill in current_skills:
            connection.execute("INSERT OR IGNORE INTO Skills (skill_name) VALUES (?)", (skill,))
            connection.execute("INSERT OR IGNORE INTO UserSkills (user_id, skill_name) VALUES (?, ?)", (user_id, skill))
        connection.commit()
    finally:
        connection.close()


def save_dynamic_role_skills(role, skills_list):
    """
    Saves newly discovered skills for custom roles into SQLite.
    """
    if not role or not skills_list:
        return
    connection = get_connection()
    for item in skills_list:
        if isinstance(item, tuple) and len(item) == 2:
            skill_name, importance = item
        elif isinstance(item, dict):
            skill_name = item.get("skill_name", item.get("skill", ""))
            importance = item.get("importance", item.get("priority", "High"))
        elif isinstance(item, str):
            skill_name = item
            importance = "High"
        else:
            continue

        skill_name = skill_name.strip()
        if not skill_name:
            continue

        connection.execute("INSERT OR IGNORE INTO Skills (skill_name) VALUES (?)", (skill_name,))
        exists = connection.execute(
            "SELECT 1 FROM RoleSkills WHERE role = ? AND skill_name = ?",
            (role, skill_name),
        ).fetchone()
        if not exists:
            connection.execute(
                "INSERT INTO RoleSkills (role, skill_name, importance) VALUES (?, ?, ?)",
                (role, skill_name, importance),
            )
    connection.commit()
    connection.close()


def get_role_skills(role):
    connection = get_connection()
    rows = connection.execute(
        "SELECT skill_name, importance FROM RoleSkills WHERE role = ? ORDER BY id",
        (role,),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_user_analyses(user_id):
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT a.id AS analysis_id, au.username AS name, COALESCE(a.target_role, au.username) AS role, a.match_percentage, a.missing_skills, COALESCE(strftime('%Y-%m-%d %H:%M:%S', a.created_at), datetime('now')) AS analysis_date, MAX(0, 30 - CAST((julianday('now') - julianday(a.created_at)) AS INTEGER)) AS days_remaining, a.keep_forever FROM Analysis a JOIN AuthUsers au ON a.user_id = au.id WHERE a.user_id = ? AND a.result_json IS NOT NULL AND a.result_json != '' ORDER BY a.created_at DESC",
            (user_id,),
        ).fetchall()
    finally:
        connection.close()
    result = []
    for r in rows:
        d = dict(r)
        d["missing_skills_display"] = ", ".join(json.loads(d["missing_skills"])) if isinstance(d.get("missing_skills"), str) else (d.get("missing_skills") or [])
        result.append(d)
    return result


def delete_user_account(user_id):
    connection = get_connection()
    try:
        connection.execute("DELETE FROM AuthUsers WHERE id = ?", (user_id,))
        connection.execute("DELETE FROM Analysis WHERE user_id = ?", (user_id,))
        connection.commit()
    finally:
        connection.close()


def get_analysis_by_id(analysis_id, user_id):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT a.*, au.username AS name FROM Analysis a JOIN AuthUsers au ON a.user_id = au.id WHERE a.id = ? AND a.user_id = ?",
            (analysis_id, user_id),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def save_full_analysis_result(user_id, name, experience_level, target_role, current_skills, match_percentage, missing_skills, recommendations, dashboard_json):
    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO Analysis (user_id, match_percentage, missing_skills, recommendations, created_at, result_json, target_role) VALUES (?, ?, ?, ?, datetime('now'), ?, ?)",
            (user_id, match_percentage, json.dumps(missing_skills), json.dumps(recommendations), dashboard_json, target_role),
        )
        connection.commit()
    finally:
        connection.close()


def purge_old_analyses(days=30):
    connection = get_connection()
    try:
        connection.execute("DELETE FROM Analysis WHERE created_at < datetime('now', '-30 days') AND keep_forever = 0")
        connection.commit()
    finally:
        connection.close()


def set_analysis_keep_forever(analysis_id, user_id, keep=1):
    connection = get_connection()
    try:
        connection.execute(
            "UPDATE Analysis SET keep_forever = ? WHERE id = ? AND user_id = ?",
            (keep, analysis_id, user_id),
        )
        connection.commit()
    finally:
        connection.close()


def delete_analysis_by_id(analysis_id, user_id):
    connection = get_connection()
    try:
        connection.execute("DELETE FROM Analysis WHERE id = ? AND user_id = ?", (analysis_id, user_id))
        connection.commit()
    finally:
        connection.close()


def create_reset_token(user_id, token, expires_hours=1):
    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO PasswordReset (user_id, token, expires_at, used) VALUES (?, ?, datetime('now', '+' || ? || ' hours'), 0)",
            (user_id, token, expires_hours),
        )
        connection.commit()
    finally:
        connection.close()


def get_reset_token(token):
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM PasswordReset WHERE token = ? AND used = 0 AND expires_at > datetime('now')",
            (token,),
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def mark_token_used(token):
    connection = get_connection()
    try:
        connection.execute("UPDATE PasswordReset SET used = 1 WHERE token = ?", (token,))
        connection.commit()
    finally:
        connection.close()


def get_all_roles():
    connection = get_connection()
    rows = connection.execute("SELECT DISTINCT role FROM RoleSkills ORDER BY role").fetchall()
    connection.close()
    return [row["role"] for row in rows]


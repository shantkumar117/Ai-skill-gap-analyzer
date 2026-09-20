import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "skill_gap.db"

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
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    connection.executescript(
        """
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


def save_analysis(name, experience_level, target_role, current_skills, match_percentage, missing_skills, recommendations):
    connection = get_connection()
    cursor = connection.execute(
        "INSERT INTO Users (name, experience_level, target_role) VALUES (?, ?, ?)",
        (name, experience_level, target_role),
    )
    user_id = cursor.lastrowid
    for skill in current_skills:
        connection.execute("INSERT OR IGNORE INTO Skills (skill_name) VALUES (?)", (skill,))
        connection.execute("INSERT INTO UserSkills (user_id, skill_name) VALUES (?, ?)", (user_id, skill))
    connection.execute(
        "INSERT INTO Analysis (user_id, match_percentage, missing_skills, recommendations) VALUES (?, ?, ?, ?)",
        (user_id, match_percentage, json.dumps(missing_skills), json.dumps(recommendations)),
    )
    connection.commit()
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


def get_all_roles():
    connection = get_connection()
    rows = connection.execute("SELECT DISTINCT role FROM RoleSkills ORDER BY role").fetchall()
    connection.close()
    return [row["role"] for row in rows]


from flask import Flask, flash, redirect, render_template, request, url_for

from database import ROLE_SKILLS, get_role_skills, init_db, save_analysis

app = Flask(__name__)
app.config["SECRET_KEY"] = "skill-gap-analyzer-development-key"

EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]


def normalize_skills(raw_skills):
    return list(dict.fromkeys(skill.strip().title() for skill in raw_skills.replace("\n", ",").split(",") if skill.strip()))


def build_recommendations(role, current_skills, missing_skills, experience_level):
    recommendations = []
    if "Git" in missing_skills:
        recommendations.append("Learn Git and GitHub basics, then practice with a small repository.")
    for skill in missing_skills:
        if skill == "REST API":
            recommendations.append("Learn REST API fundamentals and build a few CRUD endpoints.")
        elif skill in {"Django", "Spring Boot", "React"}:
            recommendations.append(f"Learn {skill} fundamentals through a small role-focused application.")
        elif skill in {"Machine Learning", "Statistics", "Pandas"}:
            recommendations.append(f"Study {skill} with a small dataset and explain your findings.")
        elif skill not in {"Git"}:
            recommendations.append(f"Practice {skill} with guided exercises and one small feature.")
    if not recommendations:
        recommendations.append(f"You are building a strong {role} foundation. Strengthen your skills with a portfolio project.")
    if experience_level == "Beginner":
        recommendations.insert(0, "Start with one skill at a time and keep short notes while practicing.")
    elif experience_level == "Advanced":
        recommendations.append("Review production patterns, testing, and deployment for each target skill.")
    return recommendations[:6]


def build_projects(role, missing_skills):
    projects = {
        "Frontend Developer": "Build a responsive portfolio website with a JavaScript task tracker.",
        "Backend Developer": "Build a Flask or Django REST API with SQLite, authentication, and tests.",
        "Full Stack Developer": "Build a full-stack job tracker with a JavaScript frontend and Python API.",
        "Data Analyst": "Analyze a public dataset and publish a dashboard with clear business insights.",
        "Data Scientist": "Train and explain a small prediction model using a clean, documented dataset.",
        "Python Developer": "Build a Python automation tool with a command-line interface and tests.",
        "Java Developer": "Build a Spring Boot CRUD service with a database and unit tests.",
        "Software Engineer": "Build a small application that demonstrates data structures, algorithms, and clean Git history.",
    }
    return [projects[role], f"Create a focused practice project that demonstrates {', '.join(missing_skills[:2]) or 'your strongest skills'}."]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "GET":
        return render_template("analyze.html", roles=ROLE_SKILLS.keys(), experience_levels=EXPERIENCE_LEVELS)

    name = request.form.get("name", "").strip()
    target_role = request.form.get("target_role", "")
    experience_level = request.form.get("experience_level", "")
    current_skills = normalize_skills(request.form.get("current_skills", ""))

    if not name or target_role not in ROLE_SKILLS or experience_level not in EXPERIENCE_LEVELS or not current_skills:
        flash("Please complete every field and add at least one skill.", "error")
        return redirect(url_for("analyze"))

    role_skills = get_role_skills(target_role)
    required_names = [item["skill_name"] for item in role_skills]
    current_lower = {skill.lower() for skill in current_skills}
    have = [skill for skill in required_names if skill.lower() in current_lower]
    missing = [skill for skill in required_names if skill.lower() not in current_lower]
    skill_lookup = {item["skill_name"]: item["importance"] for item in role_skills}
    high_priority = [skill for skill in missing if skill_lookup[skill] == "High"]
    medium_priority = [skill for skill in missing if skill_lookup[skill] == "Medium"]
    match_percentage = round((len(have) / len(required_names)) * 100)
    recommendations = build_recommendations(target_role, current_skills, missing, experience_level)
    projects = build_projects(target_role, missing)
    save_analysis(name, experience_level, target_role, current_skills, match_percentage, missing, recommendations)

    dashboard_data = {
        "name": name,
        "role": target_role,
        "experience": experience_level,
        "current_skills": current_skills,
        "required_skills": required_names,
        "have": have,
        "missing": missing,
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "match_percentage": match_percentage,
        "gap_percentage": 100 - match_percentage,
        "recommendations": recommendations,
        "projects": projects,
    }
    return render_template("dashboard.html", data=dashboard_data)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

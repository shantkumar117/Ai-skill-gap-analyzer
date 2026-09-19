# AI Skill Gap Analyzer

A beginner-friendly Flask and SQLite web application that compares a student's current technical skills with the skills required for a selected software role. It produces a match percentage, missing-skill priorities, learning recommendations, and portfolio project ideas.

## Features

- Eight predefined roles: Frontend, Backend, Full Stack, Data Analyst, Data Scientist, Python, Java, and Software Engineer.
- Simple rule-based recommendation engine that works without an API key.
- SQLite tables for users, skills, role skills, user skills, and analyses.
- Responsive dashboard with a progress bar and Chart.js doughnut chart.
- Beginner, Intermediate, and Advanced learning guidance.

## Installation and run

Open a terminal in this folder. The commands below work in Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in a browser. The database is created and seeded automatically at `database/skill_gap.db` when the application starts.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once in that terminal, then activate the environment again.

## Manual database initialization

The normal `python app.py` command initializes the database. To initialize it separately:

```powershell
python -c "from database import init_db; init_db(); print('Database initialized')"
```

## Example input

- Name: Priya Sharma
- Role: Backend Developer
- Experience: Beginner
- Current skills: Python, HTML, SQL

## Example output

- Match: 33%
- Skills you have: Python, SQL
- Missing skills: Git, REST API, Django, Docker
- High priority: REST API, Django
- Medium priority: Git, Docker
- Recommendations: Learn Git and GitHub, learn REST API fundamentals, learn Django, build a REST API project, and learn basic Docker.

The exact percentage can change if you enter more or fewer matching skills.

## How it works

1. The form sends the student's name, role, experience, and comma-separated skills to Flask.
2. Flask reads the selected role's required skills from SQLite.
3. It compares normalized skill names and calculates `matched skills / required skills * 100`.
4. Missing skills are grouped by High and Medium importance.
5. The rule-based recommendation function creates a short personalized plan.
6. The user's input and analysis are stored in SQLite, and the dashboard renders the result with Jinja templates.

## Project architecture

```text
Browser
  |
  v
Flask routes (app.py) ----> Jinja templates (templates/)
  |                                  |
  v                                  v
Database helpers (database.py)   CSS + JS + Chart.js
  |
  v
SQLite database (database/skill_gap.db)
```

## Modules used

- `flask`: routes, forms, templates, and flash messages.
- `sqlite3`: built-in Python database access.
- `pathlib`: safe database file paths.
- `json`: stores missing skills and recommendations as JSON text.

No machine-learning model is trained. The AI feature is a transparent rule-based recommendation engine, which is easier to explain in a college presentation and works offline.

## Common errors and fixes

- **`python` is not recognized:** Install Python and select “Add Python to PATH”, then reopen VS Code.
- **`No module named flask`:** Activate `venv` and run `pip install -r requirements.txt`.
- **PowerShell activation error:** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
- **Port already in use:** Stop the other Flask process or change the port in `app.py` to `app.run(debug=True, port=5001)`.
- **Database looks empty:** Stop the app and run the manual initialization command above, then restart it.

## Future enhancements

- Add login and saved dashboard history.
- Add more roles and editable role skill requirements.
- Add an optional OpenAI-compatible API behind an environment variable.
- Add export to PDF and progress tracking over time.
- Add quizzes or links to curated learning resources.

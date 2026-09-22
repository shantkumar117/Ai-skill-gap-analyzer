import json
import logging
import os
import re
import time
from urllib import request as urllib_request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import ROLE_SKILLS, get_role_skills, init_db, save_analysis, save_dynamic_role_skills, get_all_roles, create_user, get_user_by_username, get_connection, get_user_analyses, get_analysis_by_id, delete_analysis_by_id, purge_old_analyses, delete_user_account, set_analysis_keep_forever
from services.ai_service import validate_and_sanitize, generate_response

app = Flask(__name__)
app.config["SECRET_KEY"] = "skill-gap-analyzer-development-key"

EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]

SKILL_CATALOG = {
    "HTML": {
        "concepts": ["Semantic elements", "Accessibility (a11y)", "Forms & validation", "SEO basics"],
        "exercise": "Build an accessible, multi-page semantic layout with structured forms.",
        "hours": "8-10 hrs",
        "resources": "MDN Web Docs - HTML Basics, web.dev",
    },
    "CSS": {
        "concepts": ["Flexbox & CSS Grid", "Custom properties (variables)", "Responsive typography", "Transitions & animations"],
        "exercise": "Create a fully responsive multi-breakpoint layout without CSS frameworks.",
        "hours": "12-15 hrs",
        "resources": "CSS-Tricks, MDN CSS Guide, Kevin Powell tutorials",
    },
    "JavaScript": {
        "concepts": ["DOM manipulation & events", "Async/Await & Promises", "Fetch API", "ES6+ syntax & modules", "Scope & closures"],
        "exercise": "Build an interactive dynamic data dashboard fetching from a public API.",
        "hours": "20-25 hrs",
        "resources": "JavaScript.info, MDN JavaScript Guide",
    },
    "React": {
        "concepts": ["Component architecture & JSX", "Hooks (useState, useEffect, useMemo)", "State management & Context", "Component props & reusability"],
        "exercise": "Develop a interactive multi-view application with stateful filters and API integration.",
        "hours": "25-30 hrs",
        "resources": "React.dev documentation, Scrimba React Course",
    },
    "Responsive Design": {
        "concepts": ["Mobile-first design", "Fluid layouts & viewport units", "Media queries", "Responsive images & navigation"],
        "exercise": "Refactor a desktop-only web application into a seamless mobile-first experience.",
        "hours": "10-12 hrs",
        "resources": "web.dev Responsive Design, MDN Responsive Design",
    },
    "Python": {
        "concepts": ["Data structures (lists/dicts/sets)", "OOP & classes", "List comprehensions & generators", "Virtual environments & pip", "Error handling"],
        "exercise": "Develop a modular CLI tool with file parsing and comprehensive unit tests.",
        "hours": "20-25 hrs",
        "resources": "Python official docs, Real Python",
    },
    "SQL": {
        "concepts": ["Complex Joins (INNER, LEFT, FULL)", "Aggregations & GROUP BY", "Subqueries & CTEs", "Indexing & query optimization", "Database normalization"],
        "exercise": "Write analytical SQL queries to calculate business metrics on multi-table datasets.",
        "hours": "15-18 hrs",
        "resources": "SQLZoo, Mode Analytics SQL Tutorial",
    },
    "Git": {
        "concepts": ["Branching & merging workflows", "Resolving merge conflicts", "Pull requests & code reviews", "Commit hygiene & Git rebase"],
        "exercise": "Maintain a GitHub repo with multi-branch development, pull requests, and automated actions.",
        "hours": "6-8 hrs",
        "resources": "Pro Git Book, GitHub Skills interactive guides",
    },
    "REST API": {
        "concepts": ["HTTP methods (GET, POST, PUT, DELETE)", "Status codes & error handling", "Resource routing & URL design", "JSON serialization & validation", "Authentication headers"],
        "exercise": "Build a secure CRUD REST API with query parameter filtering and status handling.",
        "hours": "15-20 hrs",
        "resources": "RESTful API Design Best Practices, MDN HTTP Guide",
    },
    "Django": {
        "concepts": ["MVT (Model-View-Template) pattern", "Django ORM & migrations", "Authentication & permissions", "Django admin & forms"],
        "exercise": "Build a full-fledged database-driven web portal with user registration and CRUD models.",
        "hours": "25-30 hrs",
        "resources": "Django official documentation, Django for Beginners",
    },
    "Docker": {
        "concepts": ["Dockerfile creation & layering", "Container vs image lifecycle", "Volume persistence & port mapping", "Docker Compose multi-container setups"],
        "exercise": "Containerize a web app with its database using docker-compose and run it in an isolated container.",
        "hours": "10-15 hrs",
        "resources": "Docker official docs, Docker for Beginners by Play with Docker",
    },
    "Excel": {
        "concepts": ["Pivot tables & charts", "XLOOKUP & nested functions", "Power Query data transformation", "Conditional formatting & data validation"],
        "exercise": "Transform and clean a raw multi-sheet financial dataset into an executive summary sheet.",
        "hours": "10-12 hrs",
        "resources": "Microsoft Excel documentation, ExcelIsFun",
    },
    "Statistics": {
        "concepts": ["Descriptive statistics & distributions", "Hypothesis testing (p-values, t-tests)", "Correlation vs causation", "Confidence intervals & variance"],
        "exercise": "Perform exploratory data analysis and statistical significance testing on survey data.",
        "hours": "20-25 hrs",
        "resources": "StatQuest with Josh Starmer, Khan Academy Statistics",
    },
    "Power BI": {
        "concepts": ["Data modeling & relationships", "DAX calculations & measures", "Interactive dashboard visuals", "Data transformation in Power Query"],
        "exercise": "Create a multi-tab interactive business dashboard with dynamic date slicers.",
        "hours": "15-18 hrs",
        "resources": "Microsoft Power BI Guided Learning, SQLBI",
    },
    "Data Visualization": {
        "concepts": ["Choosing appropriate charts", "Color hierarchy & contrast", "Visual storytelling & labeling", "Matplotlib / Seaborn / Plotly"],
        "exercise": "Design an informative data story report summarizing trends with clear chart aesthetics.",
        "hours": "12-15 hrs",
        "resources": "Storytelling with Data, Fundamentals of Data Visualization by Claus Wilke",
    },
    "Machine Learning": {
        "concepts": ["Supervised vs unsupervised learning", "Scikit-Learn pipelines", "Feature engineering & scaling", "Model evaluation (Precision, Recall, ROC-AUC)", "Overfitting & regularization"],
        "exercise": "Train and evaluate a cross-validated classification model on real-world benchmark data.",
        "hours": "30-35 hrs",
        "resources": "Scikit-Learn user guide, Hands-On Machine Learning (Aurélien Géron)",
    },
    "Pandas": {
        "concepts": ["DataFrame indexing & filtering", "Handling missing values & types", "Groupby aggregations & pivot tables", "Merging & concatenating datasets", "Vectorized operations"],
        "exercise": "Clean and aggregate a complex multi-source tabular dataset into ready-to-model features.",
        "hours": "15-20 hrs",
        "resources": "Pandas official documentation, 10 Minutes to Pandas",
    },
    "Object-Oriented Programming": {
        "concepts": ["Classes, objects & constructors", "Inheritance & polymorphism", "Encapsulation & abstraction", "SOLID design principles"],
        "exercise": "Refactor a procedural script into a clean domain model using OOP and design patterns.",
        "hours": "15-18 hrs",
        "resources": "Refactoring.Guru Design Patterns, Real Python OOP Guide",
    },
    "Testing": {
        "concepts": ["Unit testing vs integration testing", "Test fixtures & assertions", "Mocking external dependencies", "Code coverage & test-driven development (TDD)"],
        "exercise": "Write a thorough test suite achieving 85%+ branch coverage on an existing codebase.",
        "hours": "12-15 hrs",
        "resources": "Pytest / Unittest documentation, TestDriven.io",
    },
    "Java": {
        "concepts": ["Java syntax & type system", "Collections Framework (List, Map, Set)", "Streams API & lambdas", "Exception handling & generics", "Memory management & JVM basics"],
        "exercise": "Build a modular console-based transaction manager using Java Collections and Streams.",
        "hours": "25-30 hrs",
        "resources": "Dev.java, Mooc.fi Java Programming Course",
    },
    "Spring Boot": {
        "concepts": ["Dependency Injection & Inversion of Control", "Spring Data JPA & Hibernate", "REST Controllers & request validation", "Application configuration & profiles"],
        "exercise": "Build a production-structured Spring Boot REST microservice with database persistence.",
        "hours": "30-35 hrs",
        "resources": "Spring.io Guides, Baeldung Spring Tutorials",
    },
    "Data Structures": {
        "concepts": ["Arrays, Linked Lists, Stacks, Queues", "Hash Tables & collision resolution", "Trees (BST, Heaps) & Graphs", "Memory layout & complexity"],
        "exercise": "Implement core data structures from scratch and evaluate their time/space bounds.",
        "hours": "25-30 hrs",
        "resources": "NeetCode, OpenDSA, Visualgo",
    },
    "Algorithms": {
        "concepts": ["Big-O time and space analysis", "Binary search & two-pointer techniques", "Recursion & backtracking", "Sorting & searching", "Dynamic programming basics"],
        "exercise": "Solve 25+ algorithmic problems focusing on optimizing time and space complexity.",
        "hours": "30-35 hrs",
        "resources": "LeetCode / HackerRank curated paths, Algorithms by Robert Sedgewick",
    },
}


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


def build_structured_recommendations(role, current_skills, missing_skills, experience_level, career_goal=""):
    """
    Generates rich, comprehensive, personalized recommendations using intelligent rule-based synthesis.
    Works entirely offline with zero external dependencies.
    """
    have_skills_str = ", ".join(current_skills) if current_skills else "None"
    missing_skills_str = ", ".join(missing_skills) if missing_skills else "None"

    # 1. Summary assessment
    if not missing_skills:
        summary = (
            f"Outstanding! You already match 100% of the core competencies for a {role} at the {experience_level} level. "
            f"Your next strategic move is deepening production expertise, system design, and building polished portfolio proof."
        )
    elif len(current_skills) > 0:
        summary = (
            f"You have a solid foundation with {have_skills_str}. For the {role} path, your main focus is bridging into {missing_skills_str}. "
            f"Leveraging your existing experience will significantly accelerate your mastery of the missing competencies."
        )
    else:
        summary = (
            f"Welcome to the {role} career journey! Starting at the {experience_level} level, focusing on high-priority foundational "
            f"skills step-by-step will give you rapid momentum and confidence."
        )

    if career_goal:
        summary += f" Tailoring your projects toward your interest in '{career_goal}' will give your profile a distinctive edge."

    # 2. Learning Pathway (Phased Roadmap)
    learning_pathway = []
    high_missing = [s for s in missing_skills if s in {"Python", "Java", "HTML", "CSS", "JavaScript", "SQL", "Git", "Data Structures"}]
    framework_missing = [s for s in missing_skills if s in {"React", "Django", "Spring Boot", "REST API", "Pandas", "Power BI", "Statistics"}]
    adv_missing = [s for s in missing_skills if s in {"Docker", "Machine Learning", "Algorithms", "Testing", "Data Visualization", "Responsive Design", "Object-Oriented Programming"}]

    # Phase 1
    phase1_tasks = []
    if "Git" in missing_skills:
        phase1_tasks.append("Master Git version control, branch management, and GitHub PR workflows.")
    for s in (high_missing or missing_skills)[:2]:
        if s != "Git":
            phase1_tasks.append(f"Build strong conceptual and practical fundamentals in {s}.")
    if not phase1_tasks:
        phase1_tasks.append(f"Review core syntax, idioms, and design principles for {role}.")
        phase1_tasks.append("Set up a clean modern development environment and tooling.")

    learning_pathway.append({
        "phase": "Phase 1: Foundations & Workflow",
        "duration": "Weeks 1–2",
        "description": "Establish essential workflow tools and core language fundamentals.",
        "tasks": phase1_tasks[:3],
    })

    # Phase 2
    phase2_tasks = []
    target_p2 = framework_missing or [s for s in missing_skills if s not in high_missing]
    for s in target_p2[:3]:
        phase2_tasks.append(f"Practice {s} by building small, modular features and integrations.")
    if not phase2_tasks:
        phase2_tasks.append(f"Implement intermediate {role} workflows and connected architecture.")
        phase2_tasks.append("Connect your components with databases and external services.")

    learning_pathway.append({
        "phase": "Phase 2: Core Stack & Integration",
        "duration": "Weeks 3–5",
        "description": "Develop hands-on competence with frameworks, APIs, and data stores.",
        "tasks": phase2_tasks[:3],
    })

    # Phase 3
    phase3_tasks = []
    target_p3 = adv_missing or [s for s in missing_skills if s not in high_missing and s not in framework_missing]
    for s in target_p3[:2]:
        phase3_tasks.append(f"Incorporate {s} into your capstone project with automated checks.")
    phase3_tasks.append(f"Build and deploy a complete capstone portfolio project for {role}.")
    phase3_tasks.append("Write clear README documentation, architecture diagrams, and test suites.")

    learning_pathway.append({
        "phase": "Phase 3: Production Polish & Portfolio",
        "duration": "Weeks 6–8",
        "description": "Apply testing, containerization, deployment, and portfolio showcase.",
        "tasks": phase3_tasks[:3],
    })

    # 3. Skill Action Plans
    skill_action_plans = []
    for skill in missing_skills:
        info = SKILL_CATALOG.get(skill, {
            "concepts": ["Core syntax & idioms", "Common design patterns", "Debugging & error handling", "Real-world best practices"],
            "exercise": f"Build a practical mini-feature demonstrating {skill} fundamentals.",
            "hours": "12-16 hrs",
            "resources": f"Official documentation and tutorials for {skill}",
        })
        skill_action_plans.append({
            "skill": skill,
            "priority": "High" if skill in {"Python", "Java", "JavaScript", "SQL", "REST API", "Data Structures", "HTML", "CSS", "Machine Learning"} else "Medium",
            "estimated_hours": info["hours"],
            "core_concepts": info["concepts"],
            "practical_exercise": info["exercise"],
            "recommended_resources": info["resources"],
        })

    # 4. Custom Portfolio Projects
    portfolio_projects = generate_custom_projects(role, current_skills, missing_skills, experience_level, career_goal)

    # 5. Interview & Career Tips
    interview_tips = [
        f"Be prepared to explain trade-offs and design decisions for technologies required in {role}.",
        f"Highlight how your existing background in {', '.join(current_skills[:3]) or 'software development'} helps you ramp up rapidly.",
        f"Prepare 2-3 stories following the STAR method (Situation, Task, Action, Result) from your hands-on projects.",
    ]
    if experience_level == "Beginner":
        interview_tips.insert(0, "Focus on showing strong problem-solving fundamentals, curiosity, and code readability.")
    elif experience_level == "Advanced":
        interview_tips.insert(0, "Focus on architectural design, scalability, automated testing, and CI/CD best practices.")

    # 6. Legacy flat list for backward compatibility
    legacy_list = build_recommendations(role, current_skills, missing_skills, experience_level)

    return {
        "summary": summary,
        "provider": "Intelligent Rule Engine",
        "learning_pathway": learning_pathway,
        "skill_action_plans": skill_action_plans,
        "portfolio_projects": portfolio_projects,
        "interview_tips": interview_tips,
        "recommendations_list": legacy_list,
    }


def generate_custom_projects(role, current_skills, missing_skills, experience_level, career_goal=""):
    """
    Designs customized project blueprints combining current and missing skills.
    """
    curr_set = {s.title() for s in current_skills}
    miss_set = {s.title() for s in missing_skills}

    projects = []

    if role == "Backend Developer":
        skills_used = list(dict.fromkeys(["Python", "SQL", "REST API", "Git"] + list(curr_set | miss_set)))[:5]
        projects.append({
            "title": "Scalable RESTful API & Service Portal",
            "difficulty": "Intermediate" if experience_level != "Beginner" else "Beginner-Friendly",
            "description": "Build an authenticated CRUD backend service with structured endpoints, relational database persistence, and robust query filtering.",
            "skills_used": skills_used,
            "key_features": ["JWT / Session Authentication", "Relational database schema with indexes", "Comprehensive automated unit tests", "Interactive API documentation"],
        })
        projects.append({
            "title": "Containerized Data Ingestion & Processing Worker",
            "difficulty": "Intermediate to Advanced",
            "description": "Develop a background task service that processes incoming data streams or webhooks, stores processed records, and runs in Docker containers.",
            "skills_used": list(dict.fromkeys(["Docker", "SQL", "Python", "Testing"] + list(miss_set)))[:5],
            "key_features": ["Docker Compose multi-service architecture", "Asynchronous task queue", "Structured JSON logging & error alerts"],
        })
    elif role == "Frontend Developer":
        skills_used = list(dict.fromkeys(["JavaScript", "HTML", "CSS", "React"] + list(curr_set | miss_set)))[:5]
        projects.append({
            "title": "Interactive Analytics & Workflow Dashboard",
            "difficulty": "Intermediate",
            "description": "Create a responsive, multi-page client application with dynamic state management, chart visualizations, and smooth user interactions.",
            "skills_used": skills_used,
            "key_features": ["Responsive flexbox/grid layout", "State management with custom hooks", "Theme switcher (Dark/Light mode)", "Client-side routing & caching"],
        })
        projects.append({
            "title": "Accessible Component Library & Style System",
            "difficulty": "Intermediate",
            "description": "Design and document a reusable set of UI components with WCAG 2.1 accessibility compliance, keyboard navigation, and unit tests.",
            "skills_used": list(dict.fromkeys(["HTML", "CSS", "JavaScript", "Responsive Design"] + list(miss_set)))[:5],
            "key_features": ["WCAG AA accessibility compliance", "Reusable button, modal, and form controls", "Interactive storybook or showcase page"],
        })
    elif role == "Full Stack Developer":
        skills_used = list(dict.fromkeys(["JavaScript", "Python", "SQL", "REST API", "React"] + list(curr_set | miss_set)))[:5]
        projects.append({
            "title": "Full-Stack Collaborative Platform",
            "difficulty": "Intermediate to Advanced",
            "description": "Develop an end-to-end web application with a responsive frontend communicating with a custom REST API backend and SQLite/PostgreSQL database.",
            "skills_used": skills_used,
            "key_features": ["User authentication & role-based access", "Full CRUD operations across relational entities", "Clean decoupled architecture with Git versioning"],
        })
        projects.append({
            "title": "SaaS Subscription & Job Application Tracker",
            "difficulty": "Intermediate",
            "description": "Build an intuitive management tool where users can track status updates, upload documents, and visualize career milestones.",
            "skills_used": list(dict.fromkeys(["React", "REST API", "SQL", "Docker"] + list(miss_set)))[:5],
            "key_features": ["Interactive kanban or table view", "Data export to CSV / JSON", "Dockerized deployment ready for cloud hosting"],
        })
    elif role in {"Data Analyst", "Data Scientist"}:
        skills_used = list(dict.fromkeys(["Python", "SQL", "Pandas", "Data Visualization", "Statistics"] + list(curr_set | miss_set)))[:5]
        projects.append({
            "title": "End-to-End Market Trends & Predictive Insights Report",
            "difficulty": "Intermediate",
            "description": "Clean, explore, and analyze an open dataset to uncover hidden patterns and produce actionable business recommendations.",
            "skills_used": skills_used,
            "key_features": ["Automated data cleaning pipeline with Pandas", "Exploratory statistical hypothesis testing", "Interactive visual dashboard with clear narrative insights"],
        })
        projects.append({
            "title": "Customer Churn / Conversion Prediction Model",
            "difficulty": "Advanced" if role == "Data Scientist" else "Intermediate",
            "description": "Train, evaluate, and interpret a machine learning model to predict user behaviors and quantify feature importances.",
            "skills_used": list(dict.fromkeys(["Machine Learning", "Statistics", "Pandas", "Python"] + list(miss_set)))[:5],
            "key_features": ["Feature engineering and scaling pipeline", "Cross-validation and confusion matrix evaluation", "Summary business presentation report"],
        })
    elif role == "Java Developer":
        skills_used = list(dict.fromkeys(["Java", "Spring Boot", "SQL", "Git", "Testing"] + list(curr_set | miss_set)))[:5]
        projects.append({
            "title": "Enterprise Spring Boot E-Commerce / Inventory Microservice",
            "difficulty": "Intermediate",
            "description": "Build a robust Java backend service with Spring Boot, JPA repository persistence, layered service architecture, and unit tests.",
            "skills_used": skills_used,
            "key_features": ["Layered controller-service-repository architecture", "Relational database integration with Hibernate", "JUnit & Mockito automated testing"],
        })
        projects.append({
            "title": "Banking / Transaction Audit Processing Engine",
            "difficulty": "Advanced",
            "description": "Create a high-reliability transaction processing system utilizing Java Streams, concurrency patterns, and error recovery.",
            "skills_used": list(dict.fromkeys(["Java", "SQL", "Object-Oriented Programming", "Testing"] + list(miss_set)))[:5],
            "key_features": ["Thread-safe transaction processing", "Custom exception hierarchy", "Comprehensive test suite with mocks"],
        })
    elif role == "Python Developer":
        skills_used = list(dict.fromkeys(["Python", "SQL", "Django", "Git", "Testing"] + list(curr_set | miss_set)))[:5]
        projects.append({
            "title": "Automated Content & Web Scraping Intelligence Platform",
            "difficulty": "Intermediate",
            "description": "Construct a modular Python application that gathers, cleans, and stores external information with structured logging and CLI commands.",
            "skills_used": skills_used,
            "key_features": ["Object-oriented architecture", "Robust exception handling and retry logic", "Automated unit tests with Pytest"],
        })
        projects.append({
            "title": "Database-Backed Django Web Portal",
            "difficulty": "Intermediate",
            "description": "Develop a complete Django application with user accounts, administrative dashboard, database migrations, and clean template rendering.",
            "skills_used": list(dict.fromkeys(["Django", "Python", "SQL", "Git"] + list(miss_set)))[:5],
            "key_features": ["Django ORM database models", "User authentication & permission decorators", "Clean Git history with branch workflow"],
        })
    else:  # Software Engineer & generic fallback
        skills_used = list(dict.fromkeys(["Data Structures", "Algorithms", "Python", "Git", "SQL"] + list(curr_set | miss_set)))[:5]
        projects.append({
            "title": "High-Performance Data Structure & Cache Engine",
            "difficulty": "Intermediate to Advanced",
            "description": "Implement custom data structures (LRU cache, Trie, or Graph router) with Big-O complexity benchmarks and automated test coverage.",
            "skills_used": skills_used,
            "key_features": ["Clean modular object-oriented design", "Benchmarked time & space complexity", "Unit test suite covering edge cases"],
        })
        projects.append({
            "title": "Distributed Task Scheduler & Execution Service",
            "difficulty": "Intermediate",
            "description": "Design an algorithm-driven task scheduler that prioritizes jobs based on resource constraints and dependencies.",
            "skills_used": list(dict.fromkeys(["Algorithms", "Git", "Python", "SQL"] + list(miss_set)))[:5],
            "key_features": ["Graph dependency resolution (Topological sort)", "Persistent state in SQL", "Clean Git documentation and architecture specs"],
        })

    return projects


def normalize_ai_step(item):
    if not isinstance(item, str):
        item = str(item)
    item = item.strip()
    if not item:
        return ""
    item = re.sub(r"^\s*(?:\d+[\.)]|[-*•])\s*", "", item)
    item = item.strip("\"'")
    item = re.sub(r"\s+", " ", item)
    if not item:
        return ""
    lower_item = item.lower().strip(".,!? ")
    if any(marker in lower_item for marker in ["full synthesis", "here is", "let's", "let ", "hello", "hi", "hey"]):
        return ""
    if re.fullmatch(r"[a-z]{1,5}", lower_item):
        return ""
    return item


def parse_ai_response(raw_response):
    if not raw_response:
        return []

    if isinstance(raw_response, list):
        items = [normalize_ai_step(item) for item in raw_response]
        return [item for item in items if item]

    if isinstance(raw_response, dict):
        for key in ("recommendations", "items", "suggestions", "plans", "recommendations_list"):
            if key in raw_response:
                return parse_ai_response(raw_response[key])
        if "content" in raw_response:
            return parse_ai_response(raw_response["content"])
        if "message" in raw_response:
            return parse_ai_response(raw_response["message"])

    text = str(raw_response).strip()
    if not text:
        return []

    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, (list, dict)):
            return parse_ai_response(parsed)
    except json.JSONDecodeError:
        pass

    if text.startswith("[") and text.endswith("]"):
        try:
            import ast

            parsed = ast.literal_eval(text)
            return parse_ai_response(parsed)
        except (ValueError, SyntaxError):
            pass

    lines = []
    for line in text.splitlines():
        cleaned = line.strip()
        cleaned = re.sub(r"^\s*(?:\d+[\.)]|[-*•])\s*", "", cleaned)
        cleaned = normalize_ai_step(cleaned)
        if cleaned:
            lines.append(cleaned)
    if lines:
        return lines

    return [normalize_ai_step(text)] if normalize_ai_step(text) else []


def parse_structured_ai_response(raw_response, fallback_func):
    """
    Parses LLM response into a validated structured recommendation object.
    Falls back gracefully if structure is incomplete.
    """
    if not raw_response:
        return fallback_func()

    data = None
    if isinstance(raw_response, dict):
        data = raw_response
    elif isinstance(raw_response, str):
        text = raw_response.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                data = parsed
            elif isinstance(parsed, list):
                # Plain list of recommendations
                fallback = fallback_func()
                cleaned_items = [normalize_ai_step(x) for x in parsed if normalize_ai_step(x)]
                if cleaned_items:
                    fallback["recommendations_list"] = cleaned_items
                return fallback
        except json.JSONDecodeError:
            pass

    if not data or not isinstance(data, dict):
        # Try extracting list from text
        items = parse_ai_response(raw_response)
        fallback = fallback_func()
        if items:
            fallback["recommendations_list"] = items
        return fallback

    fallback = fallback_func()

    summary = data.get("summary")
    if summary and isinstance(summary, str) and len(summary.strip()) > 10:
        fallback["summary"] = summary.strip()

    learning_pathway = data.get("learning_pathway")
    if isinstance(learning_pathway, list) and len(learning_pathway) > 0:
        valid_phases = []
        for p in learning_pathway:
            if isinstance(p, dict) and "phase" in p:
                valid_phases.append({
                    "phase": str(p.get("phase", "")),
                    "duration": str(p.get("duration", "2-3 weeks")),
                    "description": str(p.get("description", "")),
                    "tasks": [str(t) for t in p.get("tasks", []) if str(t).strip()],
                })
        if valid_phases:
            fallback["learning_pathway"] = valid_phases

    skill_plans = data.get("skill_action_plans")
    if isinstance(skill_plans, list) and len(skill_plans) > 0:
        valid_plans = []
        for sp in skill_plans:
            if isinstance(sp, dict) and "skill" in sp:
                valid_plans.append({
                    "skill": str(sp.get("skill", "")),
                    "priority": str(sp.get("priority", "High")),
                    "estimated_hours": str(sp.get("estimated_hours", "15 hrs")),
                    "core_concepts": [str(c) for c in sp.get("core_concepts", []) if str(c).strip()],
                    "practical_exercise": str(sp.get("practical_exercise", "")),
                    "recommended_resources": str(sp.get("recommended_resources", "")),
                })
        if valid_plans:
            fallback["skill_action_plans"] = valid_plans

    portfolio_projects = data.get("portfolio_projects")
    if isinstance(portfolio_projects, list) and len(portfolio_projects) > 0:
        valid_projects = []
        for pr in portfolio_projects:
            if isinstance(pr, dict) and "title" in pr:
                valid_projects.append({
                    "title": str(pr.get("title", "")),
                    "difficulty": str(pr.get("difficulty", "Intermediate")),
                    "description": str(pr.get("description", "")),
                    "skills_used": [str(s) for s in pr.get("skills_used", []) if str(s).strip()],
                    "key_features": [str(f) for f in pr.get("key_features", []) if str(f).strip()],
                })
        if valid_projects:
            fallback["portfolio_projects"] = valid_projects

    interview_tips = data.get("interview_tips")
    if isinstance(interview_tips, list) and len(interview_tips) > 0:
        valid_tips = [str(t) for t in interview_tips if str(t).strip()]
        if valid_tips:
            fallback["interview_tips"] = valid_tips

    recommendations_list = data.get("recommendations_list")
    if isinstance(recommendations_list, list) and len(recommendations_list) > 0:
        valid_recs = [normalize_ai_step(r) for r in recommendations_list if normalize_ai_step(r)]
        if valid_recs:
            fallback["recommendations_list"] = valid_recs

    return fallback


def generate_anthropic_recommendations(role, current_skills, missing_skills, experience_level, career_goal=""):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    fallback = lambda: build_structured_recommendations(role, current_skills, missing_skills, experience_level, career_goal)
    if not api_key:
        return fallback()

    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    prompt = (
        f"You are a top technical career advisor and software architect. "
        f"Generate a rich, structured, highly personalized skill gap analysis and action plan for a student.\n\n"
        f"Profile:\n"
        f"- Target Role: {role}\n"
        f"- Experience Level: {experience_level}\n"
        f"- Current Skills: {', '.join(current_skills) if current_skills else 'None'}\n"
        f"- Missing Required Skills: {', '.join(missing_skills) if missing_skills else 'None'}\n"
        f"- Specific Career Focus: {career_goal or 'General industry readiness'}\n\n"
        "Return ONLY a valid JSON object (no markdown fences, no explanatory text) with this exact schema:\n"
        "{\n"
        '  "summary": "1-2 sentence strategic overview of their position and how current skills help them learn missing ones",\n'
        '  "learning_pathway": [\n'
        '    {"phase": "Phase 1: Foundations", "duration": "Weeks 1-2", "description": "...", "tasks": ["task 1", "task 2"]},\n'
        '    {"phase": "Phase 2: Core Stack", "duration": "Weeks 3-5", "description": "...", "tasks": ["task 1", "task 2"]},\n'
        '    {"phase": "Phase 3: Production & Portfolio", "duration": "Weeks 6-8", "description": "...", "tasks": ["task 1", "task 2"]}\n'
        "  ],\n"
        '  "skill_action_plans": [\n'
        '    {"skill": "SkillName", "priority": "High", "estimated_hours": "15 hrs", "core_concepts": ["concept 1", "concept 2"], "practical_exercise": "...", "recommended_resources": "..."}\n'
        "  ],\n"
        '  "portfolio_projects": [\n'
        '    {"title": "...", "difficulty": "Intermediate", "description": "...", "skills_used": ["Skill1 (Existing)", "Skill2 (New)"], "key_features": ["feat 1", "feat 2"]}\n'
        "  ],\n"
        '  "interview_tips": ["tip 1", "tip 2", "tip 3"],\n'
        '  "recommendations_list": ["Action step 1", "Action step 2", "Action step 3", "Action step 4"]\n'
        "}"
    )

    payload = {
        "model": model,
        "max_tokens": 1500,
        "temperature": 0.4,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib_request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result.get("content", [])
        text = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        structured = parse_structured_ai_response(text, fallback)
        structured["provider"] = "Anthropic Claude"
        return structured
    except Exception:
        return fallback()


def generate_gemini_recommendations(role, current_skills, missing_skills, experience_level, career_goal=""):
    api_key = os.getenv("GEMINI_API_KEY")
    fallback = lambda: build_structured_recommendations(role, current_skills, missing_skills, experience_level, career_goal)
    if not api_key:
        return fallback()

    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    prompt = (
        f"You are a top technical career advisor and software architect. "
        f"Generate a rich, structured, highly personalized skill gap analysis and action plan for a student.\n\n"
        f"Profile:\n"
        f"- Target Role: {role}\n"
        f"- Experience Level: {experience_level}\n"
        f"- Current Skills: {', '.join(current_skills) if current_skills else 'None'}\n"
        f"- Missing Required Skills: {', '.join(missing_skills) if missing_skills else 'None'}\n"
        f"- Specific Career Focus: {career_goal or 'General industry readiness'}\n\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "summary": "1-2 sentence strategic overview of their position",\n'
        '  "learning_pathway": [\n'
        '    {"phase": "Phase 1: Foundations", "duration": "Weeks 1-2", "description": "...", "tasks": ["task 1", "task 2"]},\n'
        '    {"phase": "Phase 2: Core Stack", "duration": "Weeks 3-5", "description": "...", "tasks": ["task 1", "task 2"]},\n'
        '    {"phase": "Phase 3: Production & Portfolio", "duration": "Weeks 6-8", "description": "...", "tasks": ["task 1", "task 2"]}\n'
        "  ],\n"
        '  "skill_action_plans": [\n'
        '    {"skill": "SkillName", "priority": "High", "estimated_hours": "15 hrs", "core_concepts": ["concept 1", "concept 2"], "practical_exercise": "...", "recommended_resources": "..."}\n'
        "  ],\n"
        '  "portfolio_projects": [\n'
        '    {"title": "...", "difficulty": "Intermediate", "description": "...", "skills_used": ["Skill1", "Skill2"], "key_features": ["feat 1", "feat 2"]}\n'
        "  ],\n"
        '  "interview_tips": ["tip 1", "tip 2"],\n'
        '  "recommendations_list": ["Action step 1", "Action step 2", "Action step 3", "Action step 4"]\n'
        "}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1500,
            "responseMimeType": "application/json",
        },
    }
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib_request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
        candidates = result.get("candidates", [])
        if not candidates:
            return fallback()
        content = candidates[0].get("content", {}).get("parts", [])
        text = "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
        structured = parse_structured_ai_response(text, fallback)
        structured["provider"] = "Google Gemini"
        return structured
    except Exception:
        return fallback()


def generate_openai_recommendations(role, current_skills, missing_skills, experience_level, career_goal=""):
    openai_key = os.getenv("OPENAI_API_KEY")
    fallback = lambda: build_structured_recommendations(role, current_skills, missing_skills, experience_level, career_goal)
    if not openai_key:
        return fallback()

    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = (
        f"You are a top technical career advisor and software architect. "
        f"Generate a rich, structured, highly personalized skill gap analysis and action plan for a student.\n\n"
        f"Profile:\n"
        f"- Target Role: {role}\n"
        f"- Experience Level: {experience_level}\n"
        f"- Current Skills: {', '.join(current_skills) if current_skills else 'None'}\n"
        f"- Missing Required Skills: {', '.join(missing_skills) if missing_skills else 'None'}\n"
        f"- Specific Career Focus: {career_goal or 'General industry readiness'}\n\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "summary": "1-2 sentence strategic overview",\n'
        '  "learning_pathway": [\n'
        '    {"phase": "Phase 1: Foundations", "duration": "Weeks 1-2", "description": "...", "tasks": ["task 1", "task 2"]},\n'
        '    {"phase": "Phase 2: Core Stack", "duration": "Weeks 3-5", "description": "...", "tasks": ["task 1", "task 2"]},\n'
        '    {"phase": "Phase 3: Production & Portfolio", "duration": "Weeks 6-8", "description": "...", "tasks": ["task 1", "task 2"]}\n'
        "  ],\n"
        '  "skill_action_plans": [\n'
        '    {"skill": "SkillName", "priority": "High", "estimated_hours": "15 hrs", "core_concepts": ["concept 1", "concept 2"], "practical_exercise": "...", "recommended_resources": "..."}\n'
        "  ],\n"
        '  "portfolio_projects": [\n'
        '    {"title": "...", "difficulty": "Intermediate", "description": "...", "skills_used": ["Skill1", "Skill2"], "key_features": ["feat 1", "feat 2"]}\n'
        "  ],\n"
        '  "interview_tips": ["tip 1", "tip 2"],\n'
        '  "recommendations_list": ["Action step 1", "Action step 2", "Action step 3", "Action step 4"]\n'
        "}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a career mentor who outputs structured JSON."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.4,
    }

    req = urllib_request.Request(
        f"{api_base.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}",
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
        choices = result.get("choices", [])
        if not choices:
            return fallback()
        content = choices[0].get("message", {}).get("content", "")
        structured = parse_structured_ai_response(content, fallback)
        structured["provider"] = "OpenAI"
        return structured
    except Exception:
        return fallback()


def generate_ai_recommendations(role, current_skills, missing_skills, experience_level, career_goal=""):
    """
    Tries configured AI providers in sequence. Each provider gracefully falls back
    to structured synthesis only on API failure. When no provider is configured,
    returns the structured fallback.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        result = generate_anthropic_recommendations(role, current_skills, missing_skills, experience_level, career_goal)
        if result:
            return result

    if os.getenv("GEMINI_API_KEY"):
        result = generate_gemini_recommendations(role, current_skills, missing_skills, experience_level, career_goal)
        if result:
            return result

    if os.getenv("OPENAI_API_KEY"):
        result = generate_openai_recommendations(role, current_skills, missing_skills, experience_level, career_goal)
        if result:
            return result

    return build_structured_recommendations(role, current_skills, missing_skills, experience_level, career_goal)


def parse_role_skill_payload(raw_response):
    """Extracts a list of {skill_name, importance} dicts from an LLM response."""
    if not raw_response:
        return []

    data = None
    if isinstance(raw_response, list):
        data = raw_response
    elif isinstance(raw_response, dict):
        for key in ("required_skills", "skills", "role_skills", "items"):
            if key in raw_response and isinstance(raw_response[key], list):
                data = raw_response[key]
                break
        if data is None:
            data = [raw_response]
    elif isinstance(raw_response, str):
        text = raw_response.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
        try:
            parsed = json.loads(text)
            return parse_role_skill_payload(parsed)
        except json.JSONDecodeError:
            return []

    skills = []
    seen = set()
    for item in data or []:
        if isinstance(item, str):
            name, importance = item.strip(), "High"
        elif isinstance(item, dict):
            name = str(item.get("skill_name") or item.get("skill") or item.get("name") or "").strip()
            importance = str(item.get("importance") or item.get("priority") or "High").strip().title()
        else:
            continue
        if not name:
            continue
        if importance not in {"High", "Medium", "Low"}:
            importance = "High"
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        skills.append({"skill_name": name, "importance": importance})
    return skills[:12]


def infer_role_skills_from_catalog(role):
    """Best-effort local skill list for any custom role when no AI key is available."""
    role_lower = role.lower()
    catalog = [
        ("Python", "High"), ("JavaScript", "High"), ("SQL", "High"), ("Git", "Medium"),
        ("REST API", "High"), ("Docker", "Medium"), ("Testing", "Medium"),
        ("Data Structures", "Medium"), ("Linux", "Medium"),
    ]
    extra = []
    if any(token in role_lower for token in ("ai", "ml", "machine", "deep learning", "llm")):
        extra = [("Python", "High"), ("Machine Learning", "High"), ("PyTorch / TensorFlow", "High"),
                 ("Deep Learning", "High"), ("SQL", "Medium"), ("Docker", "Medium"), ("Git", "Medium")]
    elif any(token in role_lower for token in ("devops", "sre", "cloud", "platform")):
        extra = [("Linux", "High"), ("Docker", "High"), ("Kubernetes", "High"), ("CI/CD", "High"),
                 ("AWS / Cloud", "High"), ("Git", "High"), ("Terraform / IaC", "Medium"), ("Python", "Medium")]
    elif any(token in role_lower for token in ("cyber", "security", "soc", "pentest")):
        extra = [("Network Security", "High"), ("Linux", "High"), ("Python", "Medium"),
                 ("Vulnerability Assessment", "High"), ("SIEM & Log Analysis", "High"), ("Cryptography", "Medium")]
    elif any(token in role_lower for token in ("mobile", "android", "ios", "flutter", "react native")):
        extra = [("Dart / Flutter", "High"), ("JavaScript / React Native", "High"), ("REST API", "High"),
                 ("Git", "Medium"), ("State Management", "High"), ("UI/UX Design", "Medium")]
    elif any(token in role_lower for token in ("frontend", "ui", "ux")):
        extra = [("HTML", "High"), ("CSS", "High"), ("JavaScript", "High"), ("React", "High"),
                 ("Responsive Design", "High"), ("Git", "Medium")]
    elif any(token in role_lower for token in ("backend", "api", "server")):
        extra = [("Python", "High"), ("SQL", "High"), ("REST API", "High"), ("Git", "Medium"),
                 ("Docker", "Medium"), ("Testing", "Medium")]
    elif any(token in role_lower for token in ("data scientist", "scientist")):
        extra = [("Python", "High"), ("Statistics", "High"), ("Machine Learning", "High"),
                 ("Pandas", "High"), ("SQL", "Medium"), ("Data Visualization", "Medium")]
    elif any(token in role_lower for token in ("data", "analyst", "bi")):
        extra = [("Python", "High"), ("SQL", "High"), ("Excel", "High"), ("Statistics", "High"),
                 ("Power BI", "Medium"), ("Data Visualization", "High")]
    skills = extra or catalog
    return [{"skill_name": name, "importance": importance} for name, importance in skills]


def _extract_llm_text(result, provider):
    if provider == "gemini":
        candidates = result.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "\n".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if provider == "anthropic":
        return "".join(part.get("text", "") for part in result.get("content", []) if isinstance(part, dict))
    if provider == "openai":
        choices = result.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "")
    return ""


def discover_role_skills_with_ai(role, career_goal=""):
    """Ask the configured LLM which skills a given role typically requires."""
    prompt = (
        f"You are a technical hiring manager. List the 8 to 10 most important technical skills "
        f"required for the job role: '{role}'. "
        f"{'Career focus: ' + career_goal + '. ' if career_goal else ''}"
        "Return ONLY a valid JSON object with this schema:\n"
        '{"required_skills": [{"skill_name": "Skill", "importance": "High"}, '
        '{"skill_name": "Skill", "importance": "Medium"}]}\n'
        "importance must be High or Medium. No markdown, no extra text."
    )

    providers = []
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    if os.getenv("GEMINI_API_KEY"):
        providers.append("gemini")
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")

    for provider in providers:
        try:
            if provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
                model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 600,
                        "responseMimeType": "application/json",
                    },
                }
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                req = urllib_request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
                payload = {
                    "model": model,
                    "max_tokens": 800,
                    "temperature": 0.2,
                    "messages": [{"role": "user", "content": prompt}],
                }
                req = urllib_request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    method="POST",
                )
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Return only valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                }
                req = urllib_request.Request(
                    f"{api_base.rstrip('/')}/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                    method="POST",
                )

            with urllib_request.urlopen(req, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
            skills = parse_role_skill_payload(_extract_llm_text(result, provider))
            if skills:
                return skills
        except Exception:
            continue

    return infer_role_skills_from_catalog(role)


def resolve_role_skills(role, career_goal=""):
    """
    Returns required skills for any role.
    Known roles use the cached SQLite list; custom roles are discovered by AI and then cached.
    """
    cached = get_role_skills(role)
    if cached:
        return cached

    discovered = discover_role_skills_with_ai(role, career_goal)
    if discovered:
        save_dynamic_role_skills(role, discovered)
        return discovered
    return infer_role_skills_from_catalog(role)


def match_skills(current_skills, required_skills):
    """Case-insensitive match that also treats close substrings as related skills."""
    current_lower = {skill.lower() for skill in current_skills}
    have, missing = [], []
    for item in required_skills:
        name = item["skill_name"]
        target = name.lower()
        matched = any(
            current == target
            or current in target
            or target in current
            for current in current_lower
        )
        (have if matched else missing).append(name)
    return have, missing


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
    return [projects.get(role, "Build a comprehensive portfolio application demonstrating your core role competencies."), f"Create a focused practice project that demonstrates {', '.join(missing_skills[:2]) or 'your strongest skills'}."]


@app.route("/")
def index():
    return render_template("index.html")


def login_required(view_func=None, *, allow_guest=False):
    import functools
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("user_id"):
                return func(*args, **kwargs)
            if allow_guest:
                return func(*args, **kwargs)
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("register" if request.args.get("from") == "preview" else "login"))
        return wrapper
    if view_func is None:
        return decorator
    return decorator(view_func)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        if create_user(username, password_hash):
            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists. Choose a different one.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            # Read preview data BEFORE clearing session
            name = session.get("preview_name", "")
            target_role = session.get("preview_target_role", "")
            experience_level = session.get("preview_experience", "")
            current_skills_str = session.get("preview_current_skills", "")
            career_goal = session.get("preview_career_goal", "")
            custom_role = session.get("preview_custom_role", False)
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            current_skills = normalize_skills(current_skills_str) if current_skills_str else []
            if name and target_role and experience_level and current_skills:
                # Rebuild full analysis for the logged-in user
                role_skills = resolve_role_skills(target_role, career_goal)
                required_names = [item["skill_name"] for item in role_skills]
                have, missing = match_skills(current_skills, role_skills)
                skill_lookup = {item["skill_name"]: item["importance"] for item in role_skills}
                high_priority = [skill for skill in missing if skill_lookup.get(skill) == "High"]
                medium_priority = [skill for skill in missing if skill_lookup.get(skill) != "High"]
                match_percentage = round((len(have) / len(required_names)) * 100) if required_names else 0
                recommendations_data = generate_ai_recommendations(target_role, current_skills, missing, experience_level, career_goal)
                save_analysis(session.get("user_id"), name, experience_level, target_role, current_skills, match_percentage, missing, recommendations_data)
                dashboard_data = {
                    "name": name,
                    "role": target_role,
                    "experience": experience_level,
                    "career_goal": career_goal,
                    "current_skills": current_skills,
                    "required_skills": required_names,
                    "have": have,
                    "missing": missing,
                    "high_priority": high_priority,
                    "medium_priority": medium_priority,
                    "match_percentage": match_percentage,
                    "gap_percentage": 100 - match_percentage,
                    "recommendations": recommendations_data,
                    "projects": build_projects(target_role, missing),
                    "ai_mode": True,
                    "ai_provider": recommendations_data.get("provider", "AI"),
                    "custom_role": bool(custom_role),
                    "resume_review": recommendations_data.get("resume_review") if isinstance(recommendations_data, dict) else None,
                    "is_preview": False,
                }
                flash("Welcome back! Your full personalized roadmap is ready.", "success")
                return render_template("dashboard.html", data=dashboard_data)
            # If no preview was preserved, fall through to normal redirect
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("analyze"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/analysis/<int:analysis_id>/keep", methods=["POST"])
@login_required
def keep_analysis_route(analysis_id):
    set_analysis_keep_forever(analysis_id, session.get("user_id"), 1)
    flash("History kept — won’t be auto-deleted.", "info")
    return redirect(url_for("profile", _anchor="history"))


@app.route("/analysis/<int:analysis_id>/delete", methods=["POST"])
@login_required
def delete_analysis_route(analysis_id):
    delete_analysis_by_id(analysis_id, session.get("user_id"))
    flash("History deleted.", "info")
    return redirect(url_for("profile", _anchor="history"))


@app.route("/analysis/<int:analysis_id>")
@login_required
def analysis_detail(analysis_id):
    user_id = session.get("user_id")
    conn = get_connection()
    row = conn.execute("SELECT result_json FROM Analysis WHERE id = ? AND user_id = ?", (analysis_id, user_id)).fetchone()
    conn.close()
    if not row or not row["result_json"]:
        flash("Full result not found for this history.", "warning")
        return redirect(url_for("profile"))
    data = json.loads(row["result_json"])
    return render_template("dashboard.html", data=data)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST" and request.form.get("delete_account"):
        user_id = session.get("user_id")
        if user_id:
            delete_user_account(user_id)
            session.clear()
            flash("Account deleted.", "info")
            return redirect(url_for("login"))
    analyses = get_user_analyses(session.get("user_id")) if session.get("user_id") else []
    return render_template("profile.html", analyses=analyses)


@app.route("/analyze", methods=["GET", "POST"])
@login_required(allow_guest=True)
def analyze():
    preset_roles = list(ROLE_SKILLS.keys())
    saved_roles = get_all_roles()
    all_roles = list(dict.fromkeys(preset_roles + saved_roles))

    if request.method == "GET":
        load_id = request.args.get("load_id")
        if load_id:
            old = get_analysis_by_id(int(load_id), session.get("user_id")) if session.get("user_id") else None
            if old:
                session["preview_name"] = old.get("name") or session.get("username")
                session["preview_target_role"] = old.get("target_role", "")
                session["preview_experience"] = old.get("experience_level", "")
                # Reconstruct skills from UserSkills or stored analysis
                skills = []
                try:
                    conn = get_connection()
                    skill_rows = conn.execute("SELECT skill_name FROM UserSkills WHERE user_id = ?", (session.get("user_id"),)).fetchall()
                    conn.close()
                    skills = [r["skill_name"] for r in skill_rows]
                except Exception:
                    pass
                session["preview_current_skills"] = ", ".join(skills) if skills else (old.get("current_skills") or "")
                session["preview_career_goal"] = old.get("career_goal") or ""
                session["preview_custom_role"] = bool(old.get("target_role") and old.get("target_role") not in list(ROLE_SKILLS.keys()))
        return render_template(
            "analyze.html",
            roles=all_roles,
            experience_levels=EXPERIENCE_LEVELS,
            loaded=load_id is not None,
        )

    name = request.form.get("name", "").strip()
    selected_role = request.form.get("target_role", "").strip()
    custom_role = request.form.get("custom_role", "").strip()
    target_role = custom_role or selected_role
    experience_level = request.form.get("experience_level", "")
    current_skills = normalize_skills(request.form.get("current_skills", ""))
    career_goal = request.form.get("career_goal", "").strip()

    if not name or not target_role or experience_level not in EXPERIENCE_LEVELS or not current_skills:
        flash("Please complete every required field and add at least one skill.", "error")
        return redirect(url_for("analyze"))

    role_skills = resolve_role_skills(target_role, career_goal)
    required_names = [item["skill_name"] for item in role_skills]
    have, missing = match_skills(current_skills, role_skills)
    skill_lookup = {item["skill_name"]: item["importance"] for item in role_skills}
    high_priority = [skill for skill in missing if skill_lookup.get(skill) == "High"]
    medium_priority = [skill for skill in missing if skill_lookup.get(skill) != "High"]
    match_percentage = round((len(have) / len(required_names)) * 100) if required_names else 0

    is_guest = not session.get("user_id")

    recommendations_data = generate_ai_recommendations(target_role, current_skills, missing, experience_level, career_goal)
    ai_mode = True

    # Preserve user input in session so login doesn't wipe it
    session["preview_name"] = name
    session["preview_target_role"] = target_role
    session["preview_experience"] = experience_level
    session["preview_current_skills"] = ", ".join(current_skills)
    session["preview_career_goal"] = career_goal
    session["preview_custom_role"] = bool(custom_role)

    legacy_projects = build_projects(target_role, missing)

    dashboard_data = {
        "name": name,
        "role": target_role,
        "experience": experience_level,
        "career_goal": career_goal,
        "current_skills": current_skills,
        "required_skills": required_names,
        "have": have,
        "missing": missing,
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "match_percentage": match_percentage,
        "gap_percentage": 100 - match_percentage,
        "recommendations": recommendations_data,
        "projects": legacy_projects,
        "ai_mode": ai_mode,
        "ai_provider": recommendations_data.get("provider", "AI"),
        "custom_role": bool(custom_role),
        "resume_review": recommendations_data.get("resume_review") if isinstance(recommendations_data, dict) else None,
        "is_preview": is_guest,
    }

    if not is_guest:
        from database import save_full_analysis_result
        save_full_analysis_result(session.get("user_id"), name, experience_level, target_role, current_skills, match_percentage, missing, recommendations_data, json.dumps(dashboard_data))

    return render_template("dashboard.html", data=dashboard_data)


@app.route("/resume", methods=["GET", "POST"])
@login_required(allow_guest=True)
def resume_analysis():
    preset_roles = list(ROLE_SKILLS.keys())
    saved_roles = get_all_roles()
    all_roles = list(dict.fromkeys(preset_roles + saved_roles))

    if request.method == "GET":
        return render_template("resume.html", roles=all_roles)

    # Handle POST
    selected_role = request.form.get("target_role", "").strip()
    custom_role = request.form.get("custom_role", "").strip()
    target_role = custom_role or selected_role
    pasted_text = request.form.get("resume_text", "").strip()

    resume_file = request.files.get("resume_file")
    file_text = ""
    if resume_file and resume_file.filename:
        try:
            file_text = resume_file.read().decode("utf-8", errors="ignore")
        except Exception:
            pass

    resume_text = file_text or pasted_text
    if not resume_text:
        flash("Please upload a resume file or paste your resume text.", "error")
        return redirect(url_for("resume_analysis"))

    if not target_role:
        flash("Please select or enter a target role.", "error")
        return redirect(url_for("resume_analysis"))

    is_guest = not session.get("user_id")

    recommendations_data = generate_ai_resume_analysis(target_role, resume_text)

    extracted_skills = recommendations_data.get("extracted_skills", [])
    current_skills = normalize_skills(", ".join(extracted_skills)) if extracted_skills else ["Analyzed from Resume"]

    # Preserve preview like /analyze so login can rebuild full plan
    session["preview_name"] = "Resume Analysis"
    session["preview_target_role"] = target_role
    session["preview_experience"] = "Analyzed"
    session["preview_current_skills"] = ", ".join(current_skills)
    session["preview_career_goal"] = "Resume-based Assessment"
    session["preview_custom_role"] = bool(custom_role)

    role_skills = resolve_role_skills(target_role)
    required_names = [item["skill_name"] for item in role_skills]
    have, missing = match_skills(current_skills, role_skills)
    skill_lookup = {item["skill_name"]: item["importance"] for item in role_skills}
    high_priority = [skill for skill in missing if skill_lookup.get(skill) == "High"]
    medium_priority = [skill for skill in missing if skill_lookup.get(skill) != "High"]
    match_percentage = round((len(have) / len(required_names)) * 100) if required_names else 0

    dashboard_data = {
        "name": "Resume Analysis",
        "role": target_role,
        "experience": "Analyzed",
        "career_goal": "Resume-based Assessment",
        "current_skills": current_skills,
        "required_skills": required_names,
        "have": have,
        "missing": missing,
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "match_percentage": match_percentage,
        "gap_percentage": 100 - match_percentage,
        "recommendations": recommendations_data,
        "projects": build_projects(target_role, missing),
        "custom_role": bool(custom_role),
        "ai_provider": recommendations_data.get("provider", "Intelligent Rule Engine"),
        "resume_review": recommendations_data.get("resume_review"),
        "is_preview": is_guest,
    }
    if not is_guest:
        from database import save_full_analysis_result
        save_full_analysis_result(session.get("user_id"), "Resume Analysis", "Intermediate", target_role, current_skills, match_percentage, missing, recommendations_data, json.dumps(dashboard_data))
    return render_template("dashboard.html", data=dashboard_data)


@app.route("/export/pdf/<int:analysis_id>")
@login_required
def pdf_report(analysis_id):
    import json
    from flask import render_template, make_response
    conn = get_connection()
    if analysis_id > 0:
        row = conn.execute("SELECT result_json FROM Analysis WHERE id = ? AND user_id = ?", (analysis_id, session.get("user_id"))).fetchone()
    else:
        row = conn.execute("SELECT result_json FROM Analysis WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (session.get("user_id"),)).fetchone()
    conn.close()
    if not row or not row["result_json"]:
        flash("Result not found.", "warning")
        return redirect(url_for("profile"))
    data = json.loads(row["result_json"])
    html_str = render_template("report_pdf.html", data=data)
    # Try xhtml2pdf if installed; else serve HTML as download with .pdf extension
    try:
        from xhtml2pdf import pisa
        pdf_bytes = pisa.CreatePDF(html_str, dest=None)
        if pdf_bytes:
            response = make_response(pdf_bytes)
            response.headers["Content-Type"] = "application/pdf"
            response.headers["Content-Disposition"] = f"attachment; filename=skill_gap_report_{analysis_id}.pdf"
            return response
    except Exception:
        pass
    # Fallback: serve rendered HTML as .pdf download (browser can print/save)
    response = make_response(html_str)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=skill_gap_report_{analysis_id}.pdf"
    return response

@app.route("/export/csv/<int:user_id>")
def export_csv(user_id):
    from flask import Response, make_response
    import csv, io
    if not session.get("user_id"):
        return redirect(url_for("login"))
    connection = get_connection()
    row = connection.execute("SELECT * FROM Analysis WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
    connection.close()
    if not row:
        return "No data found", 404
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["field", "value"])
    writer.writerow(["name", row["user_id"]])
    writer.writerow(["match_percentage", row["match_percentage"]])
    writer.writerow(["missing_skills", row["missing_skills"]])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=analysis.csv"})


@app.route("/export/doc/<int:user_id>")
def export_doc(user_id):
    from flask import Response
    if not session.get("user_id"):
        return redirect(url_for("login"))
    connection = get_connection()
    row = connection.execute("SELECT * FROM Analysis WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
    connection.close()
    if not row:
        return "No data found", 404
    html = f"""<html><body><h1>Skill Gap Analysis</h1><p>Match: {row['match_percentage']}%</p><p>Missing: {row['missing_skills']}</p></body></html>"""
    return Response(html, mimetype="application/msword", headers={"Content-Disposition": "attachment; filename=analysis.doc"})


def generate_ai_resume_analysis(role, resume_text):
    """Combined resume review and skill gap analysis via multi-provider loop."""
    prompt = (
        f"Analyze this resume for the target role: {role}\n\n"
        f"Resume Text:\n{resume_text}\n\n"
        "Return ONLY valid JSON with this schema:\n"
        "{\n"
        '  "summary": "Strategic overview",\n'
        '  "resume_review": {\n'
        '    "strengths": ["3-4 strengths"],\n'
        '    "weaknesses": ["3-4 areas to improve"],\n'
        '    "ats_keywords_missing": ["missing keywords"],\n'
        '    "formatting_notes": "layout advice"\n'
        "  },\n"
        '  "extracted_skills": ["skills found in resume"],\n'
        '  "learning_pathway": [{"phase": "...", "duration": "...", "description": "...", "tasks": []}],\n'
        '  "skill_action_plans": [{"skill": "...", "priority": "...", "estimated_hours": "...", "core_concepts": [], "practical_exercise": "...", "recommended_resources": "..."}],\n'
        '  "portfolio_projects": [{"title": "...", "difficulty": "...", "description": "...", "skills_used": [], "key_features": []}],\n'
        '  "interview_tips": ["tip 1", "tip 2"],\n'
        '  "recommendations_list": ["action 1", "action 2"]\n'
        "}"
    )

    providers = []
    if os.getenv("ANTHROPIC_API_KEY"): providers.append("anthropic")
    if os.getenv("GEMINI_API_KEY"): providers.append("gemini")
    if os.getenv("OPENAI_API_KEY"): providers.append("openai")

    fallback = lambda: build_structured_recommendations(role, [], [], "Intermediate")

    for provider in providers:
        try:
            if provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
                model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1000, "responseMimeType": "application/json"}}
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                req = urllib_request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                with urllib_request.urlopen(req, timeout=30) as response:
                    res = json.loads(response.read().decode("utf-8"))
                content = _extract_llm_text(res, "gemini")
                structured = parse_structured_ai_response(content, fallback)
                structured["provider"] = f"Gemini ({model})"
                return structured
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
                payload = {"model": model, "max_tokens": 1200, "temperature": 0.3, "messages": [{"role": "user", "content": prompt}]}
                req = urllib_request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}, method="POST")
                with urllib_request.urlopen(req, timeout=30) as response:
                    res = json.loads(response.read().decode("utf-8"))
                content = _extract_llm_text(res, "anthropic")
                structured = parse_structured_ai_response(content, fallback)
                structured["provider"] = f"Anthropic ({model})"
                return structured
            elif provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                payload = {"model": model, "messages": [{"role": "system", "content": "Return only valid JSON."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.3}
                req = urllib_request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
                with urllib_request.urlopen(req, timeout=30) as response:
                    res = json.loads(response.read().decode("utf-8"))
                content = res.get("choices", [{}])[0].get("message", {}).get("content", "")
                structured = parse_structured_ai_response(content, fallback)
                structured["provider"] = f"OpenAI ({model})"
                return structured
        except Exception:
            continue

    return fallback()


@app.route("/assistant", methods=["POST"])
@login_required
def assistant_chat():
    user_text = request.form.get("message", "").strip()
    if not user_text:
        return {"reply": "Please ask a question."}, 400
    # Rate limiting per user
    now = time.time()
    ts = _rate_limits.get(user_id := session.get("user_id"), 0)
    if now - ts < _RATE_LIMIT_SECONDS:
        return {"reply": "Please wait before sending another message."}, 429
    _rate_limits[user_id] = now

    # Build rich context from user's saved analysis + Users/UserSkills tables
    name = session.get("username", "User")
    role = session.get("preview_target_role") or session.get("last_target_role") or ""
    experience = session.get("preview_experience") or session.get("last_experience") or ""
    current_skills = session.get("preview_current_skills") or ""
    missing_skills = "Not recorded"
    match_pct = "N/A"
    recommendations = "N/A"
    if user_id:
        try:
            conn = get_connection()
            user_row = conn.execute("SELECT * FROM Users WHERE id = ?", (user_id,)).fetchone()
            latest = conn.execute("SELECT * FROM Analysis WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
            skill_rows = conn.execute("SELECT skill_name FROM UserSkills WHERE user_id = ?", (user_id,)).fetchall()
            conn.close()
            if user_row:
                name = user_row["name"] or name
                role = user_row["target_role"] or role
                experience = user_row["experience_level"] or experience
            if skill_rows:
                seen = set()
                unique = []
                for row in skill_rows:
                    s = row["skill_name"]
                    if s and s not in seen:
                        seen.add(s)
                        unique.append(s)
                current_skills = ", ".join(unique)
            if latest:
                match_pct = latest["match_percentage"]
                missing_skills = latest["missing_skills"] or missing_skills
                rec_raw = latest["recommendations"]
                if rec_raw:
                    try:
                        rec_data = json.loads(rec_raw) if isinstance(rec_raw, str) else rec_raw
                        if isinstance(rec_data, dict):
                            rec_list = rec_data.get("recommendations_list") or rec_data.get("summary") or rec_data
                            recommendations = json.dumps(rec_list) if not isinstance(rec_list, str) else rec_list
                        else:
                            recommendations = rec_raw
                    except Exception:
                        recommendations = rec_raw
        except Exception:
            pass
    role = role or "not set yet"
    experience = experience or "not set yet"
    current_skills = current_skills or "Not recorded"
    if match_pct == "N/A":
        profile_context = (
            f"Name: {name}. Target role: {role}. Experience: {experience}. "
            f"Current skills: {current_skills}. No saved analysis yet — guide them to complete /analyze or upload a resume."
        )
    else:
        profile_context = (
            f"Name: {name}. Target role: {role}. Experience: {experience}. "
            f"Skill match: {match_pct}%. Current skills: {current_skills}. "
            f"Missing skills: {missing_skills}. Recommendations: {recommendations}."
        )
    # Conversation history from session (last 6 messages)
    conversation = session.get("ai_conversation", [])
    result = generate_response(user_text, profile_context, conversation)
    # Update conversation memory
    conversation.append({"role": "user", "text": user_text})
    conversation.append({"role": "assistant", "text": result["reply"]})
    session["ai_conversation"] = conversation[-12:]  # keep last 6 turns
    session.modified = True
    return {"reply": result["reply"], "errors": result.get("errors", [])}


@app.route("/assistant/stream")
@login_required
def assistant_stream():
    """SSE endpoint — yields the complete reply immediately, then streams word chunks."""
    user_text = request.args.get("message", "").strip()
    if not user_text:
        return Response("data: {\"reply\":\"\"}\n\n", mimetype="text/event-stream")

    # Build context from DB (same as /assistant)
    user_id = session.get("user_id")
    profile_context = _build_assistant_context(user_id, session)
    conversation = session.get("ai_conversation", [])

    # Call AI once (same endpoint that works)
    result = generate_response(user_text, profile_context, conversation)
    reply = result.get("reply", "")

    # Update session memory
    updated_conv = conversation + [{"role": "user", "text": user_text}, {"role": "assistant", "text": reply}]
    session["ai_conversation"] = updated_conv[-12:]
    session.modified = True

    def stream():
        words = reply.split(" ")
        for i, w in enumerate(words):
            prefix = "" if i == 0 else " "
            chunk = prefix + w
            yield f"data: {{\"reply\":{json.dumps(chunk)}}}\n\n"
        yield "data: {\"done\":true}\n\n"

    return Response(stream(), mimetype="text/event-stream")


def _build_assistant_context(user_id, session_obj):
    name = session_obj.get("username", "User")
    role = session_obj.get("preview_target_role") or session_obj.get("last_target_role") or ""
    experience = session_obj.get("preview_experience") or session_obj.get("last_experience") or ""
    current_skills = session_obj.get("preview_current_skills") or ""
    missing = "Not recorded"; match = "N/A"; recs = "N/A"
    if user_id:
        try:
            conn = get_connection()
            user_row = conn.execute("SELECT * FROM Users WHERE id = ?", (user_id,)).fetchone()
            latest = conn.execute("SELECT * FROM Analysis WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
            skill_rows = conn.execute("SELECT skill_name FROM UserSkills WHERE user_id = ?", (user_id,)).fetchall()
            conn.close()
            if user_row:
                name = user_row["name"] or name; role = user_row["target_role"] or role; experience = user_row["experience_level"] or experience
            if skill_rows:
                seen = set(); unique = []
                for row in skill_rows:
                    s = row["skill_name"]
                    if s and s not in seen: seen.add(s); unique.append(s)
                current_skills = ", ".join(unique)
            if latest:
                match = latest["match_percentage"]; missing = latest["missing_skills"] or missing
                rec_raw = latest["recommendations"]
                if rec_raw:
                    try:
                        d = json.loads(rec_raw) if isinstance(rec_raw, str) else rec_raw
                        recs = json.dumps(d.get("recommendations_list", d.get("summary", rec_raw))) if isinstance(d, dict) else rec_raw
                    except Exception: recs = rec_raw
        except Exception: pass
    role = role or "not set yet"; experience = experience or "not set yet"; current_skills = current_skills or "Not recorded"
    if match == "N/A":
        return f"Name: {name}. Target role: {role}. Experience: {experience}. Current skills: {current_skills}. No saved analysis yet."
    return f"Name: {name}. Target role: {role}. Experience: {experience}. Skill match: {match}%. Current skills: {current_skills}. Missing skills: {missing}. Recommendations: {recs}."


@app.route("/about")
def about():
    return render_template("about.html")


# ── In-memory rate limiting (resets on restart) ───────────────
_RATE_LIMIT_SECONDS = 5
_rate_limits = {}


@app.route("/health")
def health():
    return {"status": "ok", "ai": "gemini", "model": os.getenv("GEMINI_MODEL", "unknown")}


if __name__ == "__main__":
    init_db()
    try:
        purge_old_analyses(30)
        logger.info("Auto-purged analyses older than 30 days.")
    except Exception as e:
        logger.warning("Auto-purge failed: %s", e)
    app.run(debug=True)


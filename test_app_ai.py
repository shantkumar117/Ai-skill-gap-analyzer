import json
import unittest

import app
from database import init_db, create_user, get_connection
from werkzeug.security import generate_password_hash


class HealthEndpointTests(unittest.TestCase):
    def test_health_endpoint(self):
        client = app.app.test_client()
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")
        self.assertIn("ai", data)


class AssistantEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.test_username = "testuser"
        cls.test_password = "testpass123"
        connection = get_connection()
        connection.execute("DELETE FROM AuthUsers WHERE username = ?", (cls.test_username,))
        connection.commit()
        connection.close()
        create_user(cls.test_username, generate_password_hash(cls.test_password))

    def _login(self, client):
        return client.post("/login", data={
            "username": self.test_username,
            "password": self.test_password,
        }, follow_redirects=True)

    def test_assistant_requires_login(self):
        client = app.app.test_client()
        response = client.post("/assistant", data={"message": "hello"})
        self.assertIn(response.status_code, [302, 401, 403])

    def test_assistant_empty_message(self):
        client = app.app.test_client()
        self._login(client)
        response = client.post("/assistant", data={"message": ""})
        self.assertEqual(response.status_code, 400)

    def test_assistant_rate_limit(self):
        client = app.app.test_client()
        self._login(client)
        response1 = client.post("/assistant", data={"message": "first message"})
        self.assertIn(response1.status_code, [200, 429])
        response2 = client.post("/assistant", data={"message": "second message"})
        # Second within rate limit window should be 429 or 200 (not server error)
        self.assertIn(response2.status_code, [200, 429])

    def test_assistant_stream_endpoint(self):
        client = app.app.test_client()
        self._login(client)
        response = client.get("/assistant/stream?message=hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/event-stream")
        data = b""
        for chunk in response.iter_encoded():
            data += chunk
        text = data.decode("utf-8", errors="replace")
        self.assertIn("data:", text)

    def test_assistant_stream_requires_login(self):
        client = app.app.test_client()
        response = client.get("/assistant/stream?message=hello")
        self.assertIn(response.status_code, [302, 401, 403])


class AiRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        # Create a test user for authenticated routes
        cls.test_username = "testuser"
        cls.test_password = "testpass123"
        connection = get_connection()
        connection.execute("DELETE FROM AuthUsers WHERE username = ?", (cls.test_username,))
        connection.execute("DELETE FROM AuthUsers WHERE username = ?", ("newuser",))
        connection.commit()
        connection.close()
        create_user(cls.test_username, generate_password_hash(cls.test_password))

    def _login(self, client):
        """Helper to log in the test user."""
        return client.post("/login", data={
            "username": self.test_username,
            "password": self.test_password,
        }, follow_redirects=True)

    def test_rule_based_fallback_when_ai_is_disabled(self):
        recommendations = app.build_recommendations(
            "Backend Developer",
            ["Python", "SQL"],
            ["REST API", "Django", "Git"],
            "Beginner",
        )

        self.assertTrue(recommendations)
        self.assertIn("Start with one skill at a time", recommendations[0])
        self.assertTrue(any("REST API" in item or "Django" in item for item in recommendations))

    def test_structured_recommendations_generation(self):
        res = app.build_structured_recommendations(
            "Backend Developer",
            ["Python", "SQL"],
            ["REST API", "Docker", "Git"],
            "Beginner",
            "High-throughput APIs",
        )

        self.assertIn("summary", res)
        self.assertIn("learning_pathway", res)
        self.assertIn("skill_action_plans", res)
        self.assertIn("portfolio_projects", res)
        self.assertIn("interview_tips", res)
        self.assertIn("recommendations_list", res)

        # Verify summary mentions existing and missing skills
        self.assertIn("Python", res["summary"])
        self.assertIn("High-throughput APIs", res["summary"])

        # Verify pathway has 3 phases
        self.assertEqual(len(res["learning_pathway"]), 3)
        self.assertTrue(all("phase" in p and "tasks" in p for p in res["learning_pathway"]))

        # Verify skill plans
        skills_in_plans = [sp["skill"] for sp in res["skill_action_plans"]]
        self.assertIn("REST API", skills_in_plans)
        self.assertIn("Docker", skills_in_plans)

        # Verify portfolio projects
        self.assertTrue(len(res["portfolio_projects"]) >= 2)
        self.assertTrue(any("REST" in p["title"] or "API" in p["title"] for p in res["portfolio_projects"]))

    def test_ai_recommendation_parser_handles_string_array_response(self):
        parsed = app.parse_ai_response('["Learn REST APIs", "Build a Flask project"]')
        self.assertEqual(parsed, ["Learn REST APIs", "Build a Flask project"])

    def test_ai_recommendation_parser_handles_fenced_json_response(self):
        parsed = app.parse_ai_response('```json\n["Learn REST APIs", "Build a Flask project"]\n```')
        self.assertEqual(parsed, ["Learn REST APIs", "Build a Flask project"])

    def test_ai_recommendation_parser_handles_numbered_list_response(self):
        parsed = app.parse_ai_response('1. Learn REST APIs with a small CRUD project.\n2. Build a Flask API and practice testing.')
        self.assertEqual(parsed, ["Learn REST APIs with a small CRUD project.", "Build a Flask API and practice testing."])

    def test_parse_structured_ai_response_valid_json(self):
        sample_json = json.dumps({
            "summary": "Tailored plan for full stack progression.",
            "learning_pathway": [
                {"phase": "Phase 1: Foundations", "duration": "Weeks 1-2", "description": "Basics", "tasks": ["Task A", "Task B"]}
            ],
            "skill_action_plans": [
                {"skill": "React", "priority": "High", "estimated_hours": "20 hrs", "core_concepts": ["Hooks", "JSX"], "practical_exercise": "Build app", "recommended_resources": "React.dev"}
            ],
            "portfolio_projects": [
                {"title": "Custom Kanban App", "difficulty": "Intermediate", "description": "Manage tasks", "skills_used": ["React", "Python"], "key_features": ["Drag-and-drop", "Auth"]}
            ],
            "interview_tips": ["Focus on component lifecycle"],
            "recommendations_list": ["Step 1", "Step 2"],
        })

        fallback = lambda: app.build_structured_recommendations("Full Stack Developer", ["Python"], ["React"], "Intermediate")
        result = app.parse_structured_ai_response(sample_json, fallback)

        self.assertEqual(result["summary"], "Tailored plan for full stack progression.")
        self.assertEqual(result["learning_pathway"][0]["phase"], "Phase 1: Foundations")
        self.assertEqual(result["skill_action_plans"][0]["skill"], "React")
        self.assertEqual(result["portfolio_projects"][0]["title"], "Custom Kanban App")
        self.assertEqual(result["interview_tips"], ["Focus on component lifecycle"])

    def test_auth_flow(self):
        client = app.app.test_client()

        # POST /analyze now allows guest (preview mode), so 200 is expected
        response = client.post("/analyze", data={"name":"x","target_role":"x","experience_level":"Beginner","current_skills":"x"})
        self.assertIn(response.status_code, [200, 302])

        # Test registration
        reg_data = {
            "username": "newuser",
            "password": "password123",
            "confirm_password": "password123"
        }
        response = client.post("/register", data=reg_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Account created successfully", response.data)

        # Test login success
        login_data = {
            "username": "newuser",
            "password": "password123"
        }
        response = client.post("/login", data=login_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome back! Your full personalized roadmap is ready.", response.data)

        # Test logout
        response = client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You have been logged out", response.data)

        # Test login failure
        fail_data = {
            "username": "newuser",
            "password": "wrongpassword"
        }
        response = client.post("/login", data=fail_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid username or password", response.data)

    def test_flask_analyze_route_end_to_end(self):
        client = app.app.test_client()
        self._login(client)

        # Test GET /analyze
        response = client.get("/analyze")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Where are you headed?", response.data)

        # Test POST /analyze with preset role
        post_data = {
            "name": "Priya Sharma",
            "target_role": "Backend Developer",
            "experience_level": "Beginner",
            "current_skills": "Python, SQL",
            "career_goal": "Cloud API Engineering",
        }
        response = client.post("/analyze", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Priya Sharma", response.data)
        self.assertIn(b"Backend Developer", response.data)
        self.assertIn(b"Phased Learning Pathway", response.data)
        self.assertIn(b"Custom Portfolio Project Blueprints", response.data)

        # Test POST /analyze with custom role
        custom_post_data = {
            "name": "Alex Kim",
            "target_role": "",
            "custom_role": "AI Engineer",
            "experience_level": "Intermediate",
            "current_skills": "Python, JavaScript",
            "career_goal": "AI applications",
        }
        response = client.post("/analyze", data=custom_post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Alex Kim", response.data)
        self.assertIn(b"AI Engineer", response.data)

        # Test POST /analyze with custom role via custom_role field
        custom_post_data2 = {
            "name": "Sam Lee",
            "target_role": "Cybersecurity Analyst",
            "custom_role": "",
            "experience_level": "Advanced",
            "current_skills": "Linux, Python",
        }
        response = client.post("/analyze", data=custom_post_data2, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sam Lee", response.data)
        self.assertIn(b"Cybersecurity Analyst", response.data)

    def test_flask_resume_route(self):
        client = app.app.test_client()
        self._login(client)

        # Test GET /resume
        response = client.get("/resume")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload Resume", response.data)

        # Test POST /resume with pasted text
        post_data = {
            "target_role": "Backend Developer",
            "resume_text": "I have 2 years of Python experience, know SQL and Git. Built REST APIs with Flask.",
        }
        response = client.post("/resume", data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resume Analysis", response.data)
        self.assertIn(b"Backend Developer", response.data)

        # Test POST /resume without input should flash error
        post_data_empty = {"target_role": "Backend Developer", "resume_text": ""}
        response = client.post("/resume", data=post_data_empty, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please upload a resume", response.data)


if __name__ == "__main__":
    unittest.main()


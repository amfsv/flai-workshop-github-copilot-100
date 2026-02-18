"""
Tests for the Mergington High School Activities API.
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    """Reset the activities dict to its original state after each test."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_200(self):
        response = client.get("/activities")
        assert response.status_code == 200

    def test_returns_all_activities(self):
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_has_expected_fields(self):
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_signup_success(self):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant(self):
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_returns_400(self):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},  # already registered
        )
        assert response.status_code == 400

    def test_signup_unknown_activity_returns_404(self):
        response = client.post(
            "/activities/Unknown Activity/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_unregister_success(self):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        assert "michael@mergington.edu" in response.json()["message"]

    def test_unregister_removes_participant(self):
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_not_signed_up_returns_404(self):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "nobody@mergington.edu"},
        )
        assert response.status_code == 404

    def test_unregister_unknown_activity_returns_404(self):
        response = client.delete(
            "/activities/Unknown Activity/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 404

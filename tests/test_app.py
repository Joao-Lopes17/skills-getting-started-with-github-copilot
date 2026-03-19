import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as app_activities

client = TestClient(app)
initial_activities = copy.deepcopy(app_activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    # Arrange: ensure each test has a fresh in-memory activities state
    app_activities.clear()
    app_activities.update(copy.deepcopy(initial_activities))
    yield


def test_get_activities_returns_all_activities():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "test_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_activities[activity_name]["participants"]


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    missing_activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{missing_activity}/signup", params={"email": "nobody@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_root_redirects_to_static_index():
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/static/index.html"
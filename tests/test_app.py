import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_keys.issubset(set(data.keys()))
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_remove_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    delete_url = f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missingstudent@mergington.edu"
    delete_url = f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email, safe='')}"
    delete_url = f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}"

    # Act
    signup_response = client.post(signup_url)
    delete_response = client.delete(delete_url)

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"

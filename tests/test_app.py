from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture()
def client():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_unregister_participant_removes_email(client):
    # Arrange
    email = "test.student@mergington.edu"

    # Act
    signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
    unregister_response = client.delete(f"/activities/Chess Club/signup?email={email}")
    activities = client.get("/activities").json()

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"

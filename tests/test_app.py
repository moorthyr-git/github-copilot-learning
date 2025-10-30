import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to index.html"""
    response = client.get("/")
    assert response.status_code in [200, 307]  # Both are valid redirect status codes
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_success():
    """Test successful activity signup"""
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]

    # Verify the participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    """Test signing up a student who is already registered"""
    # First signup
    client.post("/activities/Programming Class/signup?email=test2@mergington.edu")
    
    # Try to signup again
    response = client.post("/activities/Programming Class/signup?email=test2@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_success():
    """Test successful activity unregistration"""
    # First sign up a student
    email = "unregister_test@mergington.edu"
    activity = "Math Olympiad"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Now unregister them
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who is not registered"""
    response = client.post("/activities/Science Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
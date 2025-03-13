# USED FOR TESTING THE API ENDPOINTS IN APP.PY

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../webapp/API"))) # Add API directory to path
from app import app, db 
from app import User
import pytest
import json
import base64
from django.contrib.auth.hashers import make_password


@pytest.fixture
def client():
    """Set up a Flask test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Ensure database is available for testing
            
            user1 = User(id=1, username="alice", email="alice@example.com", password=make_password("oldpassword"))
            user2 = User(id=2, username="bob", email="bob@example.com", password=make_password("oldpassword"))

            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
        yield client  # Provide the test client
        with app.app_context():
            db.drop_all()  # Clean up database after tests

def test_valid_password_reset(client):
    """Test a valid password reset request"""
    user_id = 1  # Alice's user ID

    # Make the password reset request
    response = client.post("/api/reset_password", data=json.dumps({
        "user_id": base64.b64encode(str(user_id).encode('utf-8')).decode('utf-8'),  # Base64 encoded user ID
        "new_password": "newpassword123"
    }), content_type="application/json")

    # Check response
    assert response.status_code == 200
    assert "Password reset successful" in response.get_json()["message"]

    # Verify password actually changed
    with app.app_context():
        updated_user = User.query.filter_by(id=user_id).first()
        from django.contrib.auth.hashers import check_password
        assert check_password("newpassword123", updated_user.password)

def test_invalid_user_id(client):
    """Test password reset with a non-existent user ID"""
    response = client.post("/api/reset_password", data=json.dumps({
        "user_id": base64.b64encode(str(999).encode('utf-8')).decode('utf-8'),  # Invalid user ID
        "new_password": "newpassword123"
    }), content_type="application/json")

    assert response.status_code == 404 # Check that the response is 404

def test_missing_fields(client):
    """Test password reset with missing fields"""
    response = client.post("/api/reset_password", data=json.dumps({
        "user_id": base64.b64encode(str(1).encode('utf-8')).decode('utf-8')  # Missing new_password
    }), content_type="application/json")

    assert response.status_code == 400 # Check that the response is 400

def test_empty_password(client):
    """Test password reset with an empty password"""
    response = client.post("/api/reset_password", data=json.dumps({
        "user_id": base64.b64encode(str(1).encode('utf-8')).decode('utf-8'),
        "new_password": ""  # Empty password
    }), content_type="application/json")

    assert response.status_code == 400  # Check that the response is 400

def test_non_integer_user_id(client):
    """Test password reset with a non-integer user ID"""
    response = client.post("/api/reset_password", data=json.dumps({
        "user_id": base64.b64encode("abc".encode('utf-8')).decode('utf-8'),  # Invalid ID
        "new_password": "newpassword123"
    }), content_type="application/json")

    assert response.status_code == 404 # Check that the response is 404

def test_get_valid_user(client):
    """Test retrieving a valid user"""
    response = client.get("/api/user_data?user_id=2")  # Request Bob's profile
    assert response.status_code == 200  # Check that the response is 200

    data = response.get_json()
    assert data["username"] == "bob"
    assert data["email"] == "bob@example.com"
    assert "flag" not in data  # Ensure flag is NOT returned


def test_get_user_1_with_flag(client):
    """Test retrieving user 1 (Alice) and ensuring flag is returned"""
    response = client.get("/api/user_data?user_id=1")  # Request Alice's profile
    assert response.status_code == 200 # Check that the response is 200
    data = response.get_json()
    assert data["username"] == "alice"  # Check that the username is alice
    assert data["email"] == "alice@example.com"
    assert "flag" in data


def test_get_non_existent_user(client):
    """Test requesting a user that does not exist"""
    response = client.get("/api/user_data?user_id=999")  # Invalid user ID
    assert response.status_code == 404
    assert "User not found" in response.get_json()["error"] # Check that the response is 404


def test_missing_user_id_parameter(client):
    """Test requesting user data without providing user_id"""
    response = client.get("/api/user_data")  # Missing `user_id` parameter
    assert response.status_code == 400
    assert "Missing user_id parameter" in response.get_json()["error"] # Check that the response is 400


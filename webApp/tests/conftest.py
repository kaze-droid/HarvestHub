import pytest
import os
from flask import json

@pytest.fixture
def client():
    os.environ['FLASK_ENV'] = 'testing'
    from application import app as flask_app, db
    yield flask_app.test_client()
    # Teardown and clean up
    with flask_app.app_context():
        db.drop_all()
        db.create_all()

@pytest.fixture
def signup_user(client, username="testuser", email="testuser@gmail.com", password="abc123abc123"):
    data = {
        'username': username,
        'email': email,
        'password': password,
        'confirmPassword': password
    }
    return client.post("/api/user/add", data=json.dumps(data), content_type='application/json')

@pytest.fixture
def login_user(client, email="testuser@gmail.com", password="abc123abc123"):
    data = {
        "email": email,
        "password": password,
        "remember": False
    }
    return client.post("/api/user/login", data=json.dumps(data), content_type='application/json')

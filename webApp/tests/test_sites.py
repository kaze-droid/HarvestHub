import datetime as datetime
import pytest
from flask import json

# Test all the front end routes
@pytest.mark.parametrize("entrylist",
    [
         ["/"],
         ["/predict"],
         ["/history"],
         ["/profile"]
    ])
def test_front_end_routes(client, entrylist, capsys, signup_user, login_user):
    # Create a user
    user_id = login_user.json["id"]
    with capsys.disabled():
        # Test the front end routes
        response2 = client.get(entrylist[0])
        assert response2.status_code == 200
        assert response2.headers['Content-Type'] == 'text/html; charset=utf-8'

# Test undefined routes
def test_undefined_routes(client, capsys):
    with capsys.disabled():
        response = client.get("/undefined")
        assert response.status_code == 404
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

# Test login and signup
@pytest.mark.parametrize("entrylist",
    [
        ["/signup"],
         ["/login"],
    ])
def test_signup_login(client, entrylist, capsys):
    with capsys.disabled():
        response = client.get(entrylist[0])
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
import pytest
from flask import json

#Unit Test
# Add user (sign up)
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_add_user(client, entrylist, capsys):
    url = "/api/user/add"
    data = {
        'username': entrylist[0],
        'email': entrylist[1],
        'password': entrylist[2],
        'confirmPassword': entrylist[2]
    }
    res = client.post(url, data=json.dumps(data), content_type='application/json')
    assert res.status_code == 200
    assert res.json['id']

@pytest.mark.xfail(reason="Repeated Email", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_add_user_same_email(client, entrylist, capsys):
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }
        res = client.post(ur, data=json.dumps(data), content_type='application/json')
        assert res.status_code == 200
        assert res.json['id']

        # Signup same account second time
        res2 = client.post(url, data=json.dumps(data), content_type='application/json')
        assert res2.status_code == 200

@pytest.mark.xfail(reason="Mismatch Password", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123", "abc123abc124"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123", "abc123abc122"],
    ])
def test_add_user_diff_pw(client, entrylist, capsys):
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[3]
        }
        res = client.post(url, data=json.dumps(data), content_type='application/json')
        assert res.status_code == 200
        assert res.json['id']

@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_login_user(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }

    res = client.post(url, data=json.dumps(data), content_type='application/json')

    assert res.status_code == 200
    user_id = res.json['id']

    url2 = "/api/user/login"

    data2 = {
        "email": entrylist[1],
        "password": entrylist[2],
        "remember": False
    }

    res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')

    assert res2.status_code == 200
    assert user_id == res2.json['id']

@pytest.mark.xfail(reason="User has no account", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        ["testingAccount4@gmail.com", "abc123abc123"],
        ["testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_login_user_dne(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/login"
    with capsys.disabled():
        data = {
            "email": entrylist[1],
            "password": entrylist[2],
            "remember": False
        }

        res = client.post(url, data=json.dumps(data), content_type='application/json')

        assert res.status_code == 200
        assert res.json['id']

@pytest.mark.xfail(reason="Incorrect Password", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123", "abc123abc124"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123", "abc123abc122"],
    ])
def test_login_user(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }

    res = client.post(url, data=json.dumps(data), content_type='application/json')

    assert res.status_code == 200
    user_id = res.json['id']

    url2 = "/api/user/login"

    data2 = {
        "email": entrylist[1],
        "password": entrylist[3],
        "remember": False
    }

    res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')

    assert res2.status_code == 200
    assert user_id == res2.json['id']

@pytest.mark.xfail(reason="Incorrect Email", strict=True)
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123", "testingAccount4@yahoo.com"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123", "testingAccount7@yahoo.com"],
    ])
def test_login_user(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }

    res = client.post(url, data=json.dumps(data), content_type='application/json')

    assert res.status_code == 200
    user_id = res.json['id']

    url2 = "/api/user/login"

    data2 = {
        "email": entrylist[3],
        "password": entrylist[2],
        "remember": False
    }

    res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')

    assert res2.status_code == 200
    assert user_id == res2.json['id']


@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_remove_user(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }

    res = client.post(url, data=json.dumps(data), content_type='application/json')

    assert res.status_code == 200
    user_id = res.json['id']

    url2 = "/api/user/login"

    data2 = {
        "email": entrylist[1],
        "password": entrylist[2],
        "remember": False
    }

    res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')

    assert res2.status_code == 200
    assert user_id == res2.json['id']

    url3 = "/api/user/remove"

    data3 = {
        "username": entrylist[0],
        "password": entrylist[2],
        "remember": False
    }

    res3 = client.post(url3, data=json.dumps(data3), content_type='application/json')

    assert res3.status_code == 200
    assert user_id == res3.json['id']

@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_change_username(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }

    res = client.post(url, data=json.dumps(data), content_type='application/json')

    assert res.status_code == 200
    user_id = res.json['id']

    url2 = "/api/user/login"

    data2 = {
        "email": entrylist[1],
        "password": entrylist[2],
        "remember": False
    }

    res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')

    assert res2.status_code == 200
    assert user_id == res2.json['id']

    url3 = '/api/user/changeuser'

    data = {
        "username": "newusername",
    }

    res3 = client.post(url3, data=json.dumps(data), content_type='application/json')
    
    assert res3.status_code == 200

# Test Change Password
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_change_password(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }

    res = client.post(url, data=json.dumps(data), content_type='application/json')

    assert res.status_code == 200
    user_id = res.json['id']

    url2 = "/api/user/login"

    data2 = {
        "email": entrylist[1],
        "password": entrylist[2],
        "remember": False
    }

    res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')

    assert res2.status_code == 200
    assert user_id == res2.json['id']

    url3 = '/api/user/changepw'

    data = {
        "password": "newpassword",
    }

    res3 = client.post(url3, data=json.dumps(data), content_type='application/json')
    
    assert res3.status_code == 200
    assert user_id == res3.json['id']

# Test logout
@pytest.mark.parametrize("entrylist",
    [
        ["testuser4", "testingAccount4@gmail.com", "abc123abc123"],
        ["testuser7", "testingAccount7@gmail.com", "abc123abc123"],
    ])
def test_logout_user(client, entrylist, capsys):
    # Sign up user first
    url = "/api/user/add"
    with capsys.disabled():
        data = {
            'username': entrylist[0],
            'email': entrylist[1],
            'password': entrylist[2],
            'confirmPassword': entrylist[2]
        }

    res = client.post(url, data=json.dumps(data), content_type='application/json')

    assert res.status_code == 200
    user_id = res.json['id']

    url2 = "/api/user/login"

    data2 = {
        "email": entrylist[1],
        "password": entrylist[2],
        "remember": False
    }

    res2 = client.post(url2, data=json.dumps(data2), content_type='application/json')

    assert res2.status_code == 200
    assert user_id == res2.json['id']

    url3 = '/logout'

    client.get(url3, content_type='application/json')

    # Since the user is logged out, the client will not be able to access change username
    url4 = '/api/user/changeuser'

    data = {
        "username": "newusername",
    }

    res4 = client.post(url4, data=json.dumps(data), content_type='application/json')

    assert res4.status_code == 401
    
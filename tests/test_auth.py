def test_user_signup_and_login(client):
    response = client.post(
        "/user/signup",
        data={"email": "newuser@test.com", "password": "secret123"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    login = client.post(
        "/user/login",
        data={"email": "newuser@test.com", "password": "secret123"},
        follow_redirects=False,
    )
    assert login.status_code == 302
    assert "/user/dashboard" in login.headers["Location"]


def test_user_login_invalid_credentials(client, test_user):
    response = client.post(
        "/user/login",
        data={"email": test_user.email, "password": "wrong"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/user/dashboard", follow_redirects=False)
    assert response.status_code == 302

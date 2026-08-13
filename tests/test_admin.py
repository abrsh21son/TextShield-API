def test_admin_login(client, test_admin):
    response = client.post(
        "/admin/login",
        data={"email": test_admin.email, "password": "adminpass"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "admindashboard" in response.location


def test_admin_dashboard_requires_auth(client):
    response = client.get("/admindashboard", follow_redirects=False)
    assert response.status_code == 302


def test_admin_dashboard_loads(client, test_admin):
    with client.session_transaction() as sess:
        sess["user_id"] = test_admin.id
        sess["email"] = test_admin.email
        sess["role"] = "admin"

    response = client.get("/admindashboard")
    assert response.status_code == 200

def test_demo_analyze_safe_text(client):
    response = client.post("/api/demo-analyze", json={"text": "hello world"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "result" in data


def test_demo_analyze_toxic_text(client):
    response = client.post(
        "/api/demo-analyze",
        json={"text": "you stupid idiot I hate you and want to kill"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["is_profane"] is True


def test_analyze_with_api_key(client, test_user, user_api_key):
    response = client.post(
        "/api/analyze",
        json={"text": "hello"},
        headers={"x-api-key": user_api_key},
    )
    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_analyze_missing_key(client):
    response = client.post("/api/analyze", json={"text": "hello"})
    assert response.status_code == 401

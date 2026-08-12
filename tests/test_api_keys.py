def test_generate_api_key(authed_client):
    response = authed_client.post("/api/generate-key")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["api_key"].startswith("safe_")


def test_delete_api_key(authed_client, user_api_key):
    response = authed_client.delete("/api/delete-key", json={"key": user_api_key})
    assert response.status_code == 200
    assert response.get_json()["success"] is True

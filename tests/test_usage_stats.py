def test_usage_stats(authed_client):
    response = authed_client.get("/api/usage-stats")
    assert response.status_code == 200
    data = response.get_json()
    assert "credits_remaining" in data
    assert "total_analyzed" in data
    assert "chart_data" in data


def test_usage_stats_requires_login(client):
    response = client.get("/api/usage-stats", follow_redirects=False)
    assert response.status_code == 302

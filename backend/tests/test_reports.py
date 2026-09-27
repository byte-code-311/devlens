def report_payload(**updates):
    payload = {
        "title": "Search results disappear",
        "description": "The result list becomes empty after changing the filter.",
        "expected_behavior": "The filtered results should stay visible.",
        "actual_behavior": "The result list is blank after filtering.",
        "reproduction_steps": "Open search and select a filter.",
    }
    return payload | updates


def test_create_list_and_get_report(client):
    created = client.post("/api/reports", json=report_payload())
    assert created.status_code == 201
    saved = created.json()
    assert saved["title"] == "Search results disappear"
    assert saved["id"] > 0
    assert saved["created_at"]

    assert client.get("/api/reports").json() == [saved]
    assert client.get(f"/api/reports/{saved['id']}").json() == saved


def test_report_validation_returns_field_locations(client):
    response = client.post("/api/reports", json=report_payload(title="x"))
    assert response.status_code == 422
    assert any(error["loc"][-1] == "title" for error in response.json()["detail"])


def test_report_validation_rejects_overlong_description(client):
    response = client.post(
        "/api/reports", json=report_payload(description="x" * 5001)
    )
    assert response.status_code == 422
    assert any(error["loc"][-1] == "description" for error in response.json()["detail"])


def test_report_validation_rejects_whitespace_only_required_fields(client):
    response = client.post("/api/reports", json=report_payload(description="           "))
    assert response.status_code == 422
    assert any(error["loc"][-1] == "description" for error in response.json()["detail"])


def test_get_unknown_report_returns_404(client):
    response = client.get("/api/reports/9999")
    assert response.status_code == 404

from app.services.search import seed_corpus


def test_demo_path_create_triage_open_evidence_and_feedback(client, test_sessions):
    with test_sessions() as session:
        seed_corpus(session)

    report = client.post(
        "/api/reports",
        json={
            "title": "Slow requests never finish",
            "description": "A slow request leaves the page waiting indefinitely.",
            "expected_behavior": "The page should show an error or retry option.",
            "actual_behavior": "The loading state stays visible with no explanation.",
            "reproduction_steps": "Throttle the network and load a page.",
        },
    ).json()
    triage_response = client.post(f"/api/reports/{report['id']}/triage")
    assert triage_response.status_code == 200
    triage = triage_response.json()
    assert triage["mode"] == "baseline"
    assert triage["evidence"]
    assert triage["evidence"][0]["source"].startswith("sample-app/")

    feedback_response = client.post(
        f"/api/triage/{triage['id']}/feedback",
        json={"helpful": True, "comment": "The source path gave me a place to start."},
    )
    assert feedback_response.status_code == 201
    assert feedback_response.json()["helpful"] is True

from app.schemas import Hypothesis, TriageOutput
from app.services.providers.base import ProviderError
from app.services.search import seed_corpus
from app.services.search import seed_corpus


def report_payload(**updates):
    payload = {
        "title": "Search filter clears the list",
        "description": "The list becomes empty after selecting a search filter.",
        "expected_behavior": "Matching items should remain in the result list.",
        "actual_behavior": "All results disappear after the filter is selected.",
        "reproduction_steps": "Open search and choose a filter.",
    }
    return payload | updates


def create_report(client):
    return client.post("/api/reports", json=report_payload()).json()


def test_baseline_triage_persists_cited_evidence(client, test_sessions):
    with test_sessions() as session:
        seed_corpus(session)
    report = create_report(client)
    result = client.post(f"/api/reports/{report['id']}/triage")

    assert result.status_code == 200
    triage = result.json()
    assert triage["mode"] == "baseline"
    assert triage["summary"]
    assert triage["evidence"]
    cited = {evidence_id for item in triage["hypotheses"] for evidence_id in item["evidence_ids"]}
    assert cited <= {item["id"] for item in triage["evidence"]}
    assert client.get(f"/api/reports/{report['id']}/triage").json() == [triage]


def test_no_evidence_triage_discloses_limit_and_no_cause(client):
    report = create_report(client)
    result = client.post(f"/api/reports/{report['id']}/triage")

    triage = result.json()
    assert triage["evidence"] == []
    assert triage["hypotheses"] == []
    assert triage["limitations"]


def test_triage_for_unknown_report_returns_404(client):
    assert client.post("/api/reports/9999/triage").status_code == 404


def test_feedback_is_saved_for_triage(client):
    report = create_report(client)
    triage = client.post(f"/api/reports/{report['id']}/triage").json()
    response = client.post(
        f"/api/triage/{triage['id']}/feedback",
        json={"helpful": True, "comment": "The source reference is useful."},
    )
    assert response.status_code == 201
    assert response.json()["triage_id"] == triage["id"]
    assert response.json()["helpful"] is True


def test_feedback_for_unknown_triage_returns_404(client):
    response = client.post(
        "/api/triage/9999/feedback", json={"helpful": False, "comment": None}
    )
    assert response.status_code == 404


def test_triage_rejects_provider_citation_not_retrieved(client, test_sessions):
    class InvalidCitationProvider:
        mode = "ai"

        def generate(self, report, evidence):
            return TriageOutput(
                summary="There is a possible issue.",
                hypotheses=[Hypothesis(text="An unsupported cause.", evidence_ids=[999])],
                test_suggestions=[],
                limitations=[],
            )

    with test_sessions() as session:
        seed_corpus(session)
    report = create_report(client)
    from app.api.triage import get_provider

    client.app.dependency_overrides[get_provider] = lambda: InvalidCitationProvider()
    response = client.post(f"/api/reports/{report['id']}/triage")
    assert response.status_code == 502
    assert client.get(f"/api/reports/{report['id']}").status_code == 200


def test_provider_timeout_returns_recoverable_error_and_preserves_report(client):
    class TimedOutProvider:
        mode = "ai"

        def generate(self, report, evidence):
            raise ProviderError("AI provider timed out; you can retry this triage.")

    from app.api.triage import get_provider

    client.app.dependency_overrides[get_provider] = lambda: TimedOutProvider()
    report = create_report(client)
    response = client.post(f"/api/reports/{report['id']}/triage")
    assert response.status_code == 502
    assert "retry" in response.json()["detail"]
    assert client.get(f"/api/reports/{report['id']}").status_code == 200


def test_triage_omits_cause_hypothesis_without_evidence(client):
    class UncitedProvider:
        mode = "ai"

        def generate(self, report, evidence):
            return TriageOutput(
                summary="A cause may exist.",
                hypotheses=[Hypothesis(text="The cache is broken.", evidence_ids=[])],
                test_suggestions=[],
                limitations=[],
            )

    from app.api.triage import get_provider

    client.app.dependency_overrides[get_provider] = lambda: UncitedProvider()
    report = create_report(client)
    result = client.post(f"/api/reports/{report['id']}/triage").json()
    assert result["hypotheses"] == []
    assert any("without evidence" in item for item in result["limitations"])

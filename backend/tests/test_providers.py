import pytest

from app.schemas import BugReportRead
from app.services.providers.openai_provider import OpenAIProvider, ProviderError
from app.services.providers import get_provider


class FakeResponses:
    def __init__(self, parsed=None, error=None):
        self.parsed = parsed
        self.error = error

    def parse(self, **kwargs):
        if self.error:
            raise self.error
        return type("Response", (), {"output_parsed": self.parsed})()


class FakeClient:
    def __init__(self, parsed=None, error=None):
        self.responses = FakeResponses(parsed=parsed, error=error)


def sample_report():
    return BugReportRead(
        id=1,
        title="Filter result list is blank",
        description="The search list becomes blank after choosing a filter.",
        expected_behavior="Matching results should remain visible.",
        actual_behavior="The list becomes blank.",
        reproduction_steps=None,
        created_at="2026-01-01T00:00:00Z",
    )


def test_openai_provider_rejects_malformed_empty_structured_output():
    provider = OpenAIProvider(client=FakeClient(parsed=None))
    with pytest.raises(ProviderError, match="structured triage"):
        provider.generate(sample_report(), [])


def test_openai_provider_timeout_raises_provider_error():
    provider = OpenAIProvider(client=FakeClient(error=TimeoutError("timed out")))
    with pytest.raises(ProviderError, match="timed out"):
        provider.generate(sample_report(), [])


def test_missing_credentials_selects_baseline(monkeypatch):
    from app.services import providers

    monkeypatch.setattr(providers, "get_settings", lambda: type("Settings", (), {"openai_api_key": None})())
    assert get_provider().mode == "baseline"

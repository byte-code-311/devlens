from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models import EvidenceChunk
from app.services.search import seed_corpus, search_evidence


def make_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_search_ranks_exact_case_insensitive_matches_first():
    with make_session() as session:
        seed_corpus(session)
        results = search_evidence("FILTER", session)

    assert results
    assert "filter" in results[0].text.lower()
    assert all(result.score > 0 for result in results)


def test_search_returns_stable_ids_and_locations():
    with make_session() as session:
        seed_corpus(session)
        first = search_evidence("timeout", session)
        second = search_evidence("timeout", session)

    assert first[0].id == second[0].id
    assert first[0].source
    assert first[0].location


def test_search_honors_limit_and_returns_empty_on_no_match():
    with make_session() as session:
        seed_corpus(session)
        assert len(search_evidence("cache", session, limit=2)) <= 2
        assert search_evidence("xyzzynotfoundtoken", session) == []
        assert search_evidence("the is a", session) == []


def test_seed_is_idempotent():
    with make_session() as session:
        seed_corpus(session)
        seed_corpus(session)
        count = session.query(EvidenceChunk).count()

    assert count == 12

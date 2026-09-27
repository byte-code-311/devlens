import json
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import EvidenceChunk
from ..schemas import EvidenceChunkRead

_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_STOP_WORDS = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on", "or", "the", "to", "was", "were", "with"}
_CORPUS_PATH = Path(__file__).parents[2] / "data" / "sample_corpus.json"


def tokenize(value: str) -> list[str]:
    return _TOKEN_RE.findall(value.casefold())


def seed_corpus(session: Session, corpus_path: Path = _CORPUS_PATH) -> None:
    entries = json.loads(corpus_path.read_text(encoding="utf-8"))
    existing_ids = set(session.scalars(select(EvidenceChunk.id)))
    for entry in entries:
        if entry["id"] not in existing_ids:
            session.add(EvidenceChunk(**entry))
    session.commit()


def search_evidence(
    query: str, session: Session, limit: int = 5
) -> list[EvidenceChunkRead]:
    query_tokens = [token for token in tokenize(query) if token not in _STOP_WORDS]
    if not query_tokens or limit <= 0:
        return []

    chunks = session.scalars(select(EvidenceChunk)).all()
    ranked: list[tuple[float, EvidenceChunk]] = []
    for chunk in chunks:
        text_tokens = tokenize(f"{chunk.source} {chunk.location} {chunk.text}")
        token_set = set(text_tokens)
        score = sum(2.0 if token in token_set else 0.0 for token in query_tokens)
        if score:
            ranked.append((score, chunk))

    ranked.sort(key=lambda item: (-item[0], item[1].id))
    return [
        EvidenceChunkRead(
            id=chunk.id,
            source=chunk.source,
            location=chunk.location,
            text=chunk.text,
            score=score,
        )
        for score, chunk in ranked[:limit]
    ]

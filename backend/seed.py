from app.db import Base, SessionLocal, engine
from app.models import BugReport, EvidenceChunk  # noqa: F401 - register model metadata
from app.services.search import seed_corpus


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_corpus(session)
        if session.query(BugReport).count() == 0:
            session.add_all(
                [
                    BugReport(
                        title="Search results disappear after filtering",
                        description="Changing the filter leaves the search result list blank.",
                        expected_behavior="Matching search results should remain visible.",
                        actual_behavior="The list becomes blank until the page is refreshed.",
                        reproduction_steps="Open search and select any filter.",
                    ),
                    BugReport(
                        title="Slow requests wait without a message",
                        description="A slow service call leaves the page loading for a long time.",
                        expected_behavior="The app should show a useful retry or error message.",
                        actual_behavior="The screen keeps waiting when the request is slow.",
                        reproduction_steps="Throttle the network and load a report.",
                    ),
                ]
            )
            session.commit()
    print("DevLens demo data is ready.")


if __name__ == "__main__":
    main()

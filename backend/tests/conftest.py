import asyncio

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app


class SyncASGITestClient:
    def __init__(self, application):
        self.app = application

    def request(self, method, path, **kwargs):
        async def send():
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                return await client.request(method, path, **kwargs)

        return asyncio.run(send())

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)


@pytest.fixture
def test_sessions():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_sessions = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_session():
        with testing_sessions() as session:
            yield session

    yield testing_sessions
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_sessions):
    def override_get_session():
        with test_sessions() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield SyncASGITestClient(app)
    app.dependency_overrides.clear()

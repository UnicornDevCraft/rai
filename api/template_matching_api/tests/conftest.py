from typing import TypeVar, TypeAlias, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlalchemy import Engine, create_engine, StaticPool
from sqlalchemy.orm import configure_mappers, sessionmaker, Session

from template_matching_api.db_model import Base
from template_matching_api.tests.storage import DT_STORAGE, InMemoryTemplateStorage

_T = TypeVar("_T")
YieldFixtureResult: TypeAlias = Generator[_T, None, None]


@pytest.fixture
def engine() -> Engine:
    connection = f"sqlite+pysqlite:///:memory:"
    engine = create_engine(
        connection,
        echo=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    configure_mappers()
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def sessionmaker_f(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine)


@pytest.fixture
def session(sessionmaker_f: sessionmaker[Session]) -> YieldFixtureResult[Session]:
    session = sessionmaker_f()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def app(sessionmaker_f: sessionmaker[Session]) -> YieldFixtureResult[FastAPI]:
    import template_matching_api.main as entrypoint
    import template_matching_api.api.dependencies as dependencies

    app = entrypoint.app
    app.dependency_overrides[dependencies.get_session_maker] = lambda: sessionmaker_f
    yield app


@pytest.fixture(scope="function")
def client(app: FastAPI) -> YieldFixtureResult[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function", autouse=True)
def with_test_db(
    sessionmaker_f: sessionmaker[Session], monkeypatch: MonkeyPatch
) -> YieldFixtureResult[None]:
    with monkeypatch.context() as m:
        m.setattr("template_matching_api.db.get_db", lambda: sessionmaker_f)
        yield


@pytest.fixture(scope="function", autouse=True)
def with_mock_storage(monkeypatch: MonkeyPatch) -> YieldFixtureResult[None]:
    with monkeypatch.context() as m:
        m.setattr("template_matching_api.file_storage.DocumentTemplateStorage", InMemoryTemplateStorage)
        yield
    DT_STORAGE.clear()

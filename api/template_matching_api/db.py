import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

DB_STORAGE_LOCATION = (
    Path(os.path.realpath(__file__)).parents[1] / "storage/matching_api.db"
)


def get_db() -> Engine:
    return create_engine(
        f"sqlite+pysqlite:///{DB_STORAGE_LOCATION}",
        echo=True,
    )


@contextmanager
def session_scope(session_maker: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = session_maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

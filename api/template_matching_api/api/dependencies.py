from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import sessionmaker, Session

from template_matching_api.db import get_db


def get_session_maker() -> sessionmaker[Session]:
    engine = get_db()
    return sessionmaker(bind=engine)


def get_session(session_maker: sessionmaker[Session] = Depends(get_session_maker)) -> Generator[Session, None, None]:
    with session_maker.begin() as session:
        yield session

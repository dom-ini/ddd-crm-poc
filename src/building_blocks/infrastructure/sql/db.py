from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Callable, ContextManager, Self

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm.session import Session

from building_blocks.infrastructure.sql.config import SQLALCHEMY_DB_URL

_InternalSessionFactory = Callable[[], Session]


class Base[EntityT](DeclarativeBase):
    __abstract__ = True

    def to_domain(self) -> EntityT:
        raise NotImplementedError

    @classmethod
    def from_domain(cls, entity: EntityT, **kwargs: Any) -> Self:
        raise NotImplementedError


class DbConnectionManager:
    _factory: _InternalSessionFactory | None = None
    _engine: Engine | None = None

    @classmethod
    def get_session_factory(cls, db_url: str, expire_on_commit: bool = True) -> _InternalSessionFactory:
        if not cls._factory:
            engine = create_engine(db_url, connect_args={"check_same_thread": False})
            factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=expire_on_commit)
            cls._factory = factory
            cls._engine = engine
        return cls._factory


@contextmanager
def get_db_session(db_url: str = SQLALCHEMY_DB_URL or "") -> Iterator[Session]:
    session_factory = DbConnectionManager.get_session_factory(db_url)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


SessionFactory = Callable[[], ContextManager[Session]]

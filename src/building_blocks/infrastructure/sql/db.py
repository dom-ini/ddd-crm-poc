from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Callable, ContextManager, Self

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import Session

from building_blocks.infrastructure.sql.config import SQLALCHEMY_DB_URL

_Base = declarative_base()
_InternalSessionFactory = Callable[[], Session]


class Base[EntityT](_Base):
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
    def get_session_factory(cls, db_url) -> _InternalSessionFactory:
        if not cls._factory:
            engine = create_engine(db_url, connect_args={"check_same_thread": False})
            factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            cls._factory = factory
            cls._engine = engine
        return cls._factory


@contextmanager
def get_db_session(db_url: str = SQLALCHEMY_DB_URL) -> Iterator[Session]:
    session_factory = DbConnectionManager.get_session_factory(db_url)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


SessionFactory = Callable[[], ContextManager[Session]]

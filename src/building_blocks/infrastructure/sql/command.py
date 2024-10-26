from abc import ABC
from typing import Generic, Protocol, TypeVar

from sqlalchemy.orm import Session

from building_blocks.infrastructure.exceptions import NoActiveTransaction, TransactionAlreadyActive
from building_blocks.infrastructure.sql.db import SessionFactory


class SQLRepositoryProtocol(Protocol):
    def __init__(self, db: Session) -> None: ...


RepositoryT = TypeVar("RepositoryT", bound=SQLRepositoryProtocol)


class BaseSQLUnitOfWork(ABC, Generic[RepositoryT]):
    RepositoryType: type[RepositoryT]

    def __init__(self, session_factory: SessionFactory) -> None:
        self.repository: RepositoryT | None = None
        self._session_factory = session_factory
        self._session: Session | None = None

    def begin(self) -> None:
        if self._session is not None:
            raise TransactionAlreadyActive
        with self._session_factory() as session:
            self._session = session
            self.repository = self.RepositoryType(session)
        self._session.begin()

    def commit(self) -> None:
        if self._session is None:
            raise NoActiveTransaction("No active transaction to commit")
        self._session.commit()
        self._end_session()

    def rollback(self) -> None:
        if self._session is None:
            raise NoActiveTransaction("No active transaction to rollback")
        self._session.rollback()
        self._end_session()

    def _end_session(self) -> None:
        self._session = None
        self.repository = None

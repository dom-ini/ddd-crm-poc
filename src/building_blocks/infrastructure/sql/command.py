from abc import ABC

from sqlalchemy.orm import Session

from building_blocks.infrastructure.sql.db import SessionFactory


class BaseSQLUnitOfWork[RepositoryT](ABC):
    RepositoryType: RepositoryT

    def __init__(self, session_factory: SessionFactory) -> None:
        self.repository: RepositoryT | None = None
        self._session_factory = session_factory
        self._session: Session | None = None

    def begin(self) -> None:
        self._start_session()
        self._session.begin()

    def commit(self) -> None:
        self._session.commit()
        self._end_session()

    def rollback(self) -> None:
        self._session.rollback()
        self._end_session()

    def _start_session(self) -> None:
        with self._session_factory() as session:
            self._session = session
        self.repository = self.RepositoryType(self._session)

    def _end_session(self) -> None:
        self._session = None
        self.repository = None

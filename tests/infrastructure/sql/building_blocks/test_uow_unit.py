from collections.abc import Callable, Iterator
from unittest.mock import MagicMock

import pytest
from attrs import define
from sqlalchemy.orm import Session

from building_blocks.infrastructure.exceptions import NoActiveTransaction, TransactionAlreadyActive
from building_blocks.infrastructure.sql.command import BaseSQLUnitOfWork


@define
class DummyRepository:
    session: Session


class SQLUnitOfWork(BaseSQLUnitOfWork[DummyRepository]):
    RepositoryType = DummyRepository


@pytest.fixture()
def mock_session() -> MagicMock:
    session = MagicMock(spec=Session, name="SESSION")
    return session


@pytest.fixture()
def mock_session_factory(mock_session: MagicMock) -> Iterator[MagicMock]:
    factory = MagicMock()
    factory.return_value.__enter__.return_value = mock_session
    return factory


@pytest.fixture()
def uow(mock_session_factory: Callable[[], MagicMock]) -> SQLUnitOfWork:
    return SQLUnitOfWork(session_factory=mock_session_factory)


def test_begin_starts_transaction(uow: SQLUnitOfWork, mock_session: MagicMock) -> None:
    uow.begin()

    mock_session.begin.assert_called_once()
    assert isinstance(uow.repository, DummyRepository)


def test_commit_commits_transaction(uow: SQLUnitOfWork, mock_session: MagicMock) -> None:
    uow.begin()

    uow.commit()

    mock_session.commit.assert_called_once()
    assert uow.repository is None


def test_rollback_rollbacks_transaction(uow: SQLUnitOfWork, mock_session: MagicMock) -> None:
    uow.begin()

    uow.rollback()

    mock_session.rollback.assert_called_once()
    assert uow.repository is None


def test_cannot_start_already_started_transaction(uow: SQLUnitOfWork) -> None:
    uow.begin()

    with pytest.raises(TransactionAlreadyActive):
        uow.begin()


def test_cannot_commit_without_started_transaction(uow: SQLUnitOfWork) -> None:
    with pytest.raises(NoActiveTransaction):
        uow.commit()


def test_cannot_rollback_without_started_transaction(uow: SQLUnitOfWork) -> None:
    with pytest.raises(NoActiveTransaction):
        uow.rollback()

from unittest.mock import MagicMock

import pytest
from attrs import define

from building_blocks.infrastructure.exceptions import NoActiveTransaction, TransactionAlreadyActive
from building_blocks.infrastructure.file.command import BaseFileUnitOfWork, FileLikeDB


@define
class DummyRepository:
    db: FileLikeDB


class FileUnitOfWork(BaseFileUnitOfWork[DummyRepository]):
    RepositoryType = DummyRepository

    def _get_db(self) -> FileLikeDB:
        return MagicMock()


@pytest.fixture()
def uow() -> FileUnitOfWork:
    return FileUnitOfWork(file_path="")


def test_begin_starts_transaction(uow: FileUnitOfWork) -> None:
    uow.begin()

    assert uow._is_active
    assert isinstance(uow.repository, DummyRepository)
    assert uow._snapshot is not None


def test_commit_syncs_and_closes_db(uow: FileUnitOfWork) -> None:
    uow.begin()

    uow.commit()

    assert not uow._is_active
    assert uow._snapshot is None
    uow._db.sync.assert_called_once()
    uow._db.close.assert_called_once()


def test_rollback_reverts_to_snapshot(uow: FileUnitOfWork) -> None:
    uow.begin()
    snapshot = {"key": "value"}
    uow._snapshot = snapshot

    uow.rollback()

    uow._db.clear.assert_called_once()
    uow._db.update.assert_called_with(snapshot)
    uow._db.close.assert_called_once()


def test_cannot_start_already_started_transaction(uow: FileUnitOfWork) -> None:
    uow.begin()

    with pytest.raises(TransactionAlreadyActive):
        uow.begin()


def test_cannot_commit_without_started_transaction(uow: FileUnitOfWork) -> None:
    with pytest.raises(NoActiveTransaction):
        uow.commit()


def test_cannot_rollback_without_started_transaction(uow: FileUnitOfWork) -> None:
    with pytest.raises(NoActiveTransaction):
        uow.rollback()

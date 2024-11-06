import shelve
from collections.abc import Hashable
from typing import Any

import pytest
from attrs import define

from building_blocks.application.command import BaseUnitOfWork
from building_blocks.infrastructure.file.command import BaseFileUnitOfWork, FileLikeDB
from tests.fixtures.file.db_fixtures import FILE_TEST_DATA_FOLDER

pytestmark = pytest.mark.integration

TEST_DATA_PATH = FILE_TEST_DATA_FOLDER / "test-uow"


class DummyException(Exception):
    pass


@define
class Repository:
    db: FileLikeDB

    def set(self, key: Hashable, value: Any) -> None:
        self.db[key] = value


class FileUnitOfWork(BaseFileUnitOfWork[Repository], BaseUnitOfWork):
    RepositoryType = Repository


@pytest.fixture()
def uow() -> FileUnitOfWork:
    return FileUnitOfWork(file_path=TEST_DATA_PATH)


def test_commit_transaction(uow: FileUnitOfWork) -> None:
    uow.begin()
    uow.repository.set("key1", "value1")
    uow.repository.set("key2", "value2")

    uow.commit()

    with shelve.open(TEST_DATA_PATH) as db:
        assert db["key1"] == "value1"
        assert db["key2"] == "value2"


def test_rollback_transaction(uow: FileUnitOfWork) -> None:
    uow.begin()
    uow.repository.set("key3", "value1")
    uow.repository.set("key4", "value2")

    uow.rollback()

    with shelve.open(TEST_DATA_PATH) as db:
        assert not db.get("key3")
        assert not db.get("key4")


def test_uow_context_manager(uow: FileUnitOfWork) -> None:
    with uow as uow:
        uow.repository.set("key1", "value1")
        uow.repository.set("key2", "value2")

    with shelve.open(TEST_DATA_PATH) as db:
        assert db["key1"] == "value1"
        assert db["key2"] == "value2"


def test_uow_context_manager_exception_should_rollback(uow: FileUnitOfWork) -> None:
    with uow as uow_cm:
        uow_cm.repository.set("key1", "value1")
        uow_cm.repository.set("key2", "value2")

    try:
        with uow as uow_cm:
            uow_cm.repository.set("key3", "value3")
            raise DummyException
    except DummyException:
        pass

    with shelve.open(TEST_DATA_PATH) as db:
        assert db["key1"] == "value1"
        assert db["key2"] == "value2"
        assert not db.get("key3")

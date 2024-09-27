import shelve
from abc import ABC
from pathlib import Path

from building_blocks.infrastructure.exceptions import NoActiveTransaction, TransactionAlreadyActive
from building_blocks.infrastructure.file.io import get_write_db


class BaseFileUnitOfWork[RepositoryT](ABC):
    RepositoryType: RepositoryT

    def __init__(self, file_path: Path) -> None:
        self.repository: RepositoryT | None = None
        self.db_path = file_path
        self._db: shelve.Shelf | None = None
        self._snapshot = None
        self._is_active = False

    def begin(self) -> None:
        if self._is_active:
            raise TransactionAlreadyActive
        self._db = get_write_db(self.db_path)
        self._snapshot = dict(self._db)
        self.repository = self.RepositoryType(self._db)
        self._is_active = True

    def commit(self) -> None:
        if not self._is_active:
            raise NoActiveTransaction("No active transaction to commit")
        self._db.sync()
        self._snapshot = None
        self._db.close()
        self._is_active = False

    def rollback(self) -> None:
        if not self._is_active:
            raise NoActiveTransaction("No active transaction to rollback")
        self._db.clear()
        self._db.update(self._snapshot)
        self._db.close()
        self._is_active = False


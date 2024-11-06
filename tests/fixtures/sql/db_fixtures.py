from collections.abc import Iterator
from pathlib import Path
from typing import ContextManager

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config
from sqlalchemy.orm import Session

from building_blocks.infrastructure.sql import db

SQL_TEST_DATA_FOLDER = Path(__file__).parent.parent.parent / "infrastructure/sql/test_data"
SQL_TEST_DB_URL = f"sqlite:///{SQL_TEST_DATA_FOLDER}/test.db"
SQL_MIGRATIONS_FOLDER = Path(db.__file__).parent / "alembic"


@pytest.fixture(scope="session")
def run_migrations() -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(SQL_MIGRATIONS_FOLDER.absolute()))
    alembic_cfg.set_main_option("sqlalchemy.url", SQL_TEST_DB_URL)
    alembic_upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def connection_manager() -> type[db.DbConnectionManager]:
    return db.DbConnectionManager


@pytest.fixture(scope="session")
def clear_sql_test_data() -> Iterator[None]:
    yield
    for file in SQL_TEST_DATA_FOLDER.iterdir():
        file.unlink()


@pytest.fixture(scope="session")
def session_factory(
    connection_manager: type[db.DbConnectionManager], run_migrations: None, clear_sql_test_data: None
) -> Iterator[ContextManager[Session]]:
    factory = connection_manager.get_session_factory(SQL_TEST_DB_URL, expire_on_commit=False)
    yield factory
    connection_manager._engine.dispose()

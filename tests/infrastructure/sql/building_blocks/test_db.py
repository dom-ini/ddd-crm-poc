from sqlalchemy.orm import Session, sessionmaker

from building_blocks.infrastructure.sql.db import DbConnectionManager, get_db_session
from tests.infrastructure.sql.conftest import SQL_TEST_DB_URL


def test_get_db_session_returns_session() -> None:
    with get_db_session(SQL_TEST_DB_URL) as db:
        assert isinstance(db, Session)


def test_get_session_factory_returns_session_factory(connection_manager: type[DbConnectionManager]) -> None:
    factory = connection_manager.get_session_factory(SQL_TEST_DB_URL)

    assert isinstance(factory, sessionmaker)


def test_get_session_factory_does_not_recreate_factory_when_already_created(
    connection_manager: type[DbConnectionManager],
) -> None:
    factory_1 = connection_manager.get_session_factory(SQL_TEST_DB_URL)
    factory_2 = connection_manager.get_session_factory(SQL_TEST_DB_URL)

    assert factory_1 is factory_2

from collections.abc import Callable, Iterator
from typing import ContextManager
from uuid import uuid4

import pytest
from attrs import define
from sqlalchemy.orm import Session

from building_blocks.application.command import BaseUnitOfWork
from building_blocks.infrastructure.sql.command import BaseSQLUnitOfWork
from sales.domain.value_objects.product import Product
from sales.infrastructure.sql.opportunity.models import ProductModel

pytestmark = pytest.mark.integration


class DummyException(Exception):
    pass


@define
class Repository:
    db: Session

    def add(self, id: str, value: str) -> None:
        product = Product(name=value)
        obj = ProductModel.from_domain(entity=product)
        obj.id = id
        self.db.add(obj)

    def remove(self, id: str) -> None:
        obj = self.db.get(ProductModel, id)
        self.db.delete(obj)


class SQLUnitOfWork(BaseSQLUnitOfWork[Repository], BaseUnitOfWork):
    RepositoryType = Repository


@pytest.fixture()
def product_id() -> str:
    return str(uuid4())


@pytest.fixture()
def uow(session_factory: Callable[[], ContextManager[Session]]) -> SQLUnitOfWork:
    return SQLUnitOfWork(session_factory=session_factory)


@pytest.fixture()
def remove_product(product_id: str, session_factory: Callable[[], ContextManager[Session]]) -> Iterator[None]:
    yield
    with session_factory() as db:
        product = db.get(ProductModel, product_id)
        if product is None:
            return
        db.delete(product)
        db.commit()


@pytest.mark.usefixtures("remove_product")
def test_commit_transaction(
    uow: SQLUnitOfWork, product_id: str, session_factory: Callable[[], ContextManager[Session]]
) -> None:
    uow.begin()
    uow.repository.add(id=product_id, value="some product")

    uow.commit()

    with session_factory() as db:
        product = db.get(ProductModel, product_id)
        assert product is not None
        assert product.id == product_id


def test_rollback_transaction(
    uow: SQLUnitOfWork, product_id: str, session_factory: Callable[[], ContextManager[Session]]
) -> None:
    uow.begin()
    uow.repository.add(id=product_id, value="some product")

    uow.rollback()

    with session_factory() as db:
        product = db.get(ProductModel, product_id)
        assert product is None


@pytest.mark.usefixtures("remove_product")
def test_uow_context_manager(
    uow: SQLUnitOfWork, product_id: str, session_factory: Callable[[], ContextManager[Session]]
) -> None:
    with uow as uow:
        uow.repository.add(id=product_id, value="some product")

    with session_factory() as db:
        product = db.get(ProductModel, product_id)
        assert product is not None
        assert product.id == product_id


def test_uow_context_manager_exception_should_rollback(
    uow: SQLUnitOfWork, product_id: str, session_factory: Callable[[], ContextManager[Session]]
) -> None:
    try:
        with uow as uow:
            uow.repository.add(id=product_id, value="some product")
            raise DummyException
    except DummyException:
        pass

    with session_factory() as db:
        product = db.get(ProductModel, product_id)
        assert product is None

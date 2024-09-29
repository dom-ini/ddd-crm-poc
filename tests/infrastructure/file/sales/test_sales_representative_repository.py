from uuid import uuid4

import pytest
from attrs import define

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.infrastructure.file.sales_representative.repository import SalesRepresentativeFileRepository

pytestmark = pytest.mark.integration


@define
class DummySalesRep:
    id: str
    first_name: str


@pytest.fixture(scope="session")
def sales_rep() -> DummySalesRep:
    return DummySalesRep(id=str(uuid4()), first_name="some id")


@pytest.fixture(scope="session")
def sr_repo() -> SalesRepresentativeFileRepository:
    return SalesRepresentativeFileRepository(db={})


@pytest.fixture()
def create_sales_rep(sr_repo: SalesRepresentativeFileRepository, sales_rep: DummySalesRep) -> None:
    sr_repo.create(sales_rep)


@pytest.mark.usefixtures("create_sales_rep")
def test_create_and_get(sr_repo: SalesRepresentativeFileRepository, sales_rep: DummySalesRep) -> None:
    fetched_rep = sr_repo.get(sales_rep.id)

    assert fetched_rep is not None
    assert fetched_rep.id == sales_rep.id


def test_get_should_return_none_if_not_found(
    sr_repo: SalesRepresentativeFileRepository,
) -> None:
    fetched_rep = sr_repo.get("invalid id")

    assert fetched_rep is None


def test_create_with_existing_id_should_fail(
    sr_repo: SalesRepresentativeFileRepository, sales_rep: DummySalesRep
) -> None:
    with pytest.raises(ObjectAlreadyExists):
        sr_repo.create(sales_rep)


def test_update(sr_repo: SalesRepresentativeFileRepository, sales_rep: DummySalesRep) -> None:
    new_first_name = "Mariusz"
    updated_sales_rep = DummySalesRep(id=sales_rep.id, first_name=new_first_name)

    sr_repo.update(updated_sales_rep)

    fetched_sales_rep = sr_repo.get(sales_rep.id)
    assert fetched_sales_rep.first_name == new_first_name

from uuid import uuid4

import pytest
from attrs import define

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from customer_management.infrastructure.file.customer.repository import CustomerFileRepository

pytestmark = pytest.mark.integration


@define
class DummyCustomer:
    id: str
    relation_manager_id: str


@pytest.fixture(scope="session")
def customer() -> DummyCustomer:
    return DummyCustomer(id=str(uuid4()), relation_manager_id="some id")


@pytest.fixture(scope="session")
def customer_repo() -> CustomerFileRepository:
    return CustomerFileRepository(db={})


@pytest.fixture()
def create_customer(customer_repo: CustomerFileRepository, customer: DummyCustomer) -> None:
    customer_repo.create(customer)


@pytest.mark.usefixtures("create_customer")
def test_create_and_get(customer_repo: CustomerFileRepository, customer: DummyCustomer) -> None:
    fetched_customer = customer_repo.get(customer.id)

    assert fetched_customer is not None
    assert fetched_customer.id == customer.id


def test_get_should_return_none_if_not_found(
    customer_repo: CustomerFileRepository,
) -> None:
    fetched_customer = customer_repo.get("invalid id")

    assert fetched_customer is None


def test_create_with_existing_id_should_fail(customer_repo: CustomerFileRepository, customer: DummyCustomer) -> None:
    with pytest.raises(ObjectAlreadyExists):
        customer_repo.create(customer)


def test_update(customer_repo: CustomerFileRepository, customer: DummyCustomer) -> None:
    new_salesman_id = "new id"
    updated_customer = DummyCustomer(id=customer.id, relation_manager_id=new_salesman_id)

    customer_repo.update(updated_customer)

    fetched_customer = customer_repo.get(customer.id)
    assert fetched_customer.relation_manager_id == new_salesman_id

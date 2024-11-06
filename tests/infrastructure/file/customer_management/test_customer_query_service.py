from collections.abc import Sequence

import pytest

from building_blocks.application.filters import FilterCondition, FilterConditionType
from customer_management.application.command_model import ContactPersonCreateModel
from customer_management.application.query_model import CustomerReadModel
from customer_management.infrastructure.file.customer.query_service import CustomerFileQueryService
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from tests.fixtures.file.db_fixtures import FILE_CUSTOMER_TEST_DATA_PATH


@pytest.fixture()
def all_customers(
    customer_1: CustomerReadModel,
    customer_2: CustomerReadModel,
    customer_3: CustomerReadModel,
) -> Sequence[CustomerReadModel]:
    return (customer_1, customer_2, customer_3)


@pytest.fixture()
def query_service() -> CustomerFileQueryService:
    return CustomerFileQueryService(customers_file_path=FILE_CUSTOMER_TEST_DATA_PATH)


def test_get_customer(query_service: CustomerFileQueryService, customer_1: CustomerReadModel) -> None:
    customer = query_service.get(customer_id=customer_1.id)

    assert customer is not None
    assert customer.id == customer_1.id


def test_get_all(
    query_service: CustomerFileQueryService,
    all_customers: Sequence[CustomerReadModel],
) -> None:
    customers = query_service.get_all()

    fetched_customers_ids = set(customer.id for customer in customers)
    customers_ids = set(customer.id for customer in all_customers)
    assert fetched_customers_ids == customers_ids


def test_get_filtered(
    query_service: CustomerFileQueryService,
    customer_1: CustomerReadModel,
    customer_2: CustomerReadModel,
    representative_1: SalesRepresentativeReadModel,
) -> None:
    filters = [
        FilterCondition(
            field="relation_manager_id",
            value=representative_1.id,
            condition_type=FilterConditionType.EQUALS,
        )
    ]
    customers = query_service.get_filtered(filters)

    fetched_customers_ids = set(customer.id for customer in customers)
    assert fetched_customers_ids == {customer_1.id, customer_2.id}


def test_get_contact_persons(
    query_service: CustomerFileQueryService,
    customer_1: CustomerReadModel,
    contact_person: ContactPersonCreateModel,
) -> None:
    contact_persons = query_service.get_contact_persons(customer_id=customer_1.id)

    fetched_person = contact_persons[0]
    assert fetched_person.first_name == contact_person.first_name
    assert fetched_person.last_name == contact_person.last_name
    assert fetched_person.job_title == contact_person.job_title
    assert fetched_person.preferred_language.code == contact_person.preferred_language.code
    assert fetched_person.contact_methods[0].value == contact_person.contact_methods[0].value


@pytest.mark.parametrize("method_name", ["get", "get_contact_persons"])
def test_methods_should_return_none_if_not_found(query_service: CustomerFileQueryService, method_name: str) -> None:
    customer = getattr(query_service, method_name)(customer_id="invalid id")

    assert customer is None

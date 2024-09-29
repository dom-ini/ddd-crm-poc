from collections.abc import Iterator, Sequence

import pytest

from building_blocks.application.filters import FilterCondition, FilterConditionType
from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.command_model import (
    AddressDataCreateUpdateModel,
    CompanyInfoCreateUpdateModel,
    ContactMethodCreateUpdateModel,
    ContactPersonCreateModel,
    CountryCreateUpdateModel,
    CustomerCreateModel,
    LanguageCreateUpdateModel,
)
from customer_management.application.query_model import CustomerReadModel
from customer_management.infrastructure.file.customer.command import CustomerFileUnitOfWork
from customer_management.infrastructure.file.customer.query_service import CustomerFileQueryService
from tests.infrastructure.file.conftest import TEST_DATA_FOLDER

CUSTOMER_QUERY_DB_FILE = "test-query-customer"
TEST_DATA_PATH = TEST_DATA_FOLDER / CUSTOMER_QUERY_DB_FILE


@pytest.fixture(scope="session")
def command_use_case() -> CustomerCommandUseCase:
    uow = CustomerFileUnitOfWork(file_path=TEST_DATA_PATH)
    command_use_case = CustomerCommandUseCase(customer_uow=uow)
    return command_use_case


@pytest.fixture(scope="session")
def address() -> AddressDataCreateUpdateModel:
    country = CountryCreateUpdateModel(name="Polska", code="pl")
    return AddressDataCreateUpdateModel(
        country=country,
        street="Street",
        street_no="123",
        postal_code="11222",
        city="City",
    )


@pytest.fixture(scope="session")
def contact_person() -> ContactPersonCreateModel:
    language = LanguageCreateUpdateModel(name="english", code="en")
    contact_method = ContactMethodCreateUpdateModel(type="email", value="email@example.com", is_preferred=True)
    return ContactPersonCreateModel(
        first_name="Jan",
        last_name="Kowalski",
        job_title="CEO",
        preferred_language=language,
        contact_methods=[contact_method],
    )


@pytest.fixture(scope="session", autouse=True)
def customer_1(
    command_use_case: CustomerCommandUseCase,
    salesman_1_id: str,
    address: AddressDataCreateUpdateModel,
    contact_person: ContactPersonCreateModel,
) -> CustomerReadModel:
    company_info = CompanyInfoCreateUpdateModel(
        name="Company 1",
        industry="automotive",
        size="medium",
        legal_form="limited",
        address=address,
    )
    data = CustomerCreateModel(relation_manager_id=salesman_1_id, company_info=company_info)
    customer = command_use_case.create(customer_data=data)

    command_use_case.create_contact_person(
        customer_id=customer.id,
        editor_id=customer.relation_manager_id,
        data=contact_person,
    )

    return customer


@pytest.fixture(scope="session", autouse=True)
def customer_2(
    command_use_case: CustomerCommandUseCase,
    salesman_1_id: str,
    address: AddressDataCreateUpdateModel,
) -> CustomerReadModel:
    company_info = CompanyInfoCreateUpdateModel(
        name="Company 2",
        industry="agriculture",
        size="small",
        legal_form="partnership",
        address=address,
    )
    data = CustomerCreateModel(relation_manager_id=salesman_1_id, company_info=company_info)
    customer = command_use_case.create(customer_data=data)
    return customer


@pytest.fixture(scope="session", autouse=True)
def customer_3(
    command_use_case: CustomerCommandUseCase,
    salesman_2_id: str,
    address: AddressDataCreateUpdateModel,
) -> CustomerReadModel:
    company_info = CompanyInfoCreateUpdateModel(
        name="Company 3",
        industry="technology",
        size="large",
        legal_form="other",
        address=address,
    )
    data = CustomerCreateModel(relation_manager_id=salesman_2_id, company_info=company_info)
    customer = command_use_case.create(customer_data=data)
    return customer


@pytest.fixture()
def all_customers(
    customer_1: CustomerReadModel,
    customer_2: CustomerReadModel,
    customer_3: CustomerReadModel,
) -> Sequence[CustomerReadModel]:
    return (customer_1, customer_2, customer_3)


@pytest.fixture(scope="session", autouse=True)
def clean_data() -> Iterator[None]:
    yield
    for file in TEST_DATA_FOLDER.iterdir():
        if file.name.startswith(CUSTOMER_QUERY_DB_FILE):
            file.unlink()


@pytest.fixture()
def query_service() -> CustomerFileQueryService:
    return CustomerFileQueryService(customers_file_path=TEST_DATA_PATH)


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
    salesman_1_id: str,
) -> None:
    filters = [
        FilterCondition(
            field="relation_manager_id",
            value=salesman_1_id,
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

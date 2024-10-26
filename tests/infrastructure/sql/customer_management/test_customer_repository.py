import pytest
from sqlalchemy.orm import Session

from building_blocks.application.exceptions import InvalidData
from building_blocks.infrastructure.exceptions import ObjectAlreadyExists, ServerError
from customer_management.domain.entities.customer.customer import Customer
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.company_segment import CompanySegment
from customer_management.domain.value_objects.contact_method import ContactMethod
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.industry import Industry
from customer_management.domain.value_objects.language import Language
from customer_management.infrastructure.sql.customer.repository import CustomerSQLRepository

pytestmark = pytest.mark.integration


@pytest.fixture()
def customer_repo(session: Session) -> CustomerSQLRepository:
    return CustomerSQLRepository(session)


@pytest.fixture()
def invalid_country() -> Country:
    return Country(code="invalid", name="invalid")


@pytest.fixture()
def invalid_language() -> Language:
    return Language(code="invalid", name="invalid")


@pytest.fixture()
def contact_method() -> ContactMethod:
    contact_method = ContactMethod(type="email", value="some_email@example.com", is_preferred=True)
    return contact_method


@pytest.fixture()
def address(country: Country) -> Address:
    address = Address(country=country, street="Testowa", street_no="123", postal_code="11222", city="Testowo")
    return address


@pytest.fixture()
def address_with_invalid_country(invalid_country: Country) -> Address:
    address = Address(country=invalid_country, street="Testowa", street_no="123", postal_code="11222", city="Testowo")
    return address


@pytest.fixture()
def company_info(address: Address) -> CompanyInfo:
    company_info = CompanyInfo(
        name="company",
        industry=Industry(name="agriculture"),
        segment=CompanySegment(size="large", legal_form="limited"),
        address=address,
    )
    return company_info


@pytest.fixture()
def company_info_with_invalid_country(address_with_invalid_country: Address) -> CompanyInfo:
    company_info = CompanyInfo(
        name="company",
        industry=Industry(name="agriculture"),
        segment=CompanySegment(size="large", legal_form="limited"),
        address=address_with_invalid_country,
    )
    return company_info


@pytest.fixture()
def customer(company_info: CompanyInfo) -> Customer:
    customer = Customer(id="some id", relation_manager_id="salesman", company_info=company_info)
    return customer


@pytest.fixture()
def customer_with_contact_persons(
    company_info: CompanyInfo, language: Language, contact_method: ContactMethod
) -> Customer:
    customer = Customer(id="some id", relation_manager_id="salesman", company_info=company_info)
    customer.add_contact_person(
        editor_id=customer.relation_manager_id,
        contact_person_id="contact person 1",
        first_name="Jan",
        last_name="Kowalski",
        job_title="CEO",
        preferred_language=language,
        contact_methods=(contact_method,),
    )
    return customer


@pytest.fixture()
def customer_with_invalid_country(company_info_with_invalid_country: CompanyInfo) -> Customer:
    customer = Customer(id="some id", relation_manager_id="salesman", company_info=company_info_with_invalid_country)
    return customer


@pytest.fixture()
def customer_with_invalid_language(
    company_info: CompanyInfo, invalid_language: Language, contact_method: ContactMethod
) -> Customer:
    customer = Customer(id="some id", relation_manager_id="salesman", company_info=company_info)
    customer.add_contact_person(
        editor_id=customer.relation_manager_id,
        contact_person_id="contact person 1",
        first_name="Jan",
        last_name="Kowalski",
        job_title="CEO",
        preferred_language=invalid_language,
        contact_methods=(contact_method,),
    )
    return customer


def test_create_and_get(customer_repo: CustomerSQLRepository, customer_with_contact_persons: Customer) -> None:
    customer_repo.create(customer_with_contact_persons)

    fetched_customer = customer_repo.get(customer_with_contact_persons.id)

    assert fetched_customer is not None
    assert fetched_customer.id == customer_with_contact_persons.id


def test_get_should_return_none_if_not_found(
    customer_repo: CustomerSQLRepository,
) -> None:
    fetched_customer = customer_repo.get("invalid id")

    assert fetched_customer is None


def test_create_with_existing_id_should_fail(
    customer_repo: CustomerSQLRepository, customer_with_contact_persons: Customer
) -> None:
    customer_repo.create(customer_with_contact_persons)

    with pytest.raises(ObjectAlreadyExists):
        customer_repo.create(customer_with_contact_persons)


def test_update(customer_repo: CustomerSQLRepository, customer: Customer) -> None:
    new_salesman_id = "new salesman id"
    customer_repo.create(customer)
    customer.update(editor_id=customer.relation_manager_id, relation_manager_id=new_salesman_id)

    customer_repo.update(customer)

    fetched_customer = customer_repo.get(customer.id)
    assert fetched_customer.relation_manager_id == new_salesman_id


def test_update_updates_company_info(
    customer_repo: CustomerSQLRepository, customer: Customer, company_info: CompanyInfo
) -> None:
    new_company_name = "new company name"
    customer_repo.create(customer)
    new_company_info = CompanyInfo(
        name=new_company_name,
        industry=company_info.industry,
        segment=company_info.segment,
        address=company_info.address,
    )
    customer.update(editor_id=customer.relation_manager_id, company_info=new_company_info)

    customer_repo.update(customer)

    fetched_customer = customer_repo.get(customer.id)
    assert fetched_customer.company_info.name == new_company_name


def test_update_creates_contact_persons_if_did_not_exist(
    customer_repo: CustomerSQLRepository, customer_with_contact_persons: Customer
) -> None:
    customer_repo.create(customer_with_contact_persons)

    customer_repo.update(customer_with_contact_persons)
    customer_repo.db.flush()

    fetched_customer = customer_repo.get(customer_with_contact_persons.id)
    contact_person = fetched_customer.contact_persons[0]
    assert contact_person.id == customer_with_contact_persons.contact_persons[0].id
    assert contact_person.contact_methods == customer_with_contact_persons.contact_persons[0].contact_methods


def test_update_updates_contact_persons(
    customer_repo: CustomerSQLRepository,
    customer_with_contact_persons: Customer,
    language: Language,
    contact_method: ContactMethod,
) -> None:
    manager_id = customer_with_contact_persons.relation_manager_id
    contact_person_id = customer_with_contact_persons.contact_persons[0].id
    new_contact_person_id = "new contact person"
    new_first_name = "New first name"
    new_contact_method = ContactMethod(type="phone", value="+48123123123", is_preferred=True)
    customer_repo.create(customer_with_contact_persons)
    customer_repo.update(customer_with_contact_persons)
    customer_repo.db.flush()

    customer_with_contact_persons.add_contact_person(
        editor_id=manager_id,
        contact_person_id=new_contact_person_id,
        first_name="Piotr",
        last_name="Nowak",
        job_title="CTO",
        preferred_language=language,
        contact_methods=(contact_method,),
    )
    customer_with_contact_persons.update_contact_person(
        editor_id=manager_id,
        contact_person_id=new_contact_person_id,
        first_name=new_first_name,
        contact_methods=(new_contact_method,),
    )
    customer_with_contact_persons.remove_contact_person(editor_id=manager_id, id_to_remove=contact_person_id)

    customer_repo.update(customer_with_contact_persons)
    customer_repo.db.flush()

    fetched_customer = customer_repo.get(customer_with_contact_persons.id)
    contact_person = fetched_customer.contact_persons[0]
    assert contact_person_id not in tuple(person.id for person in fetched_customer.contact_persons)
    assert contact_person.id == new_contact_person_id
    assert contact_person.contact_methods == (new_contact_method,)


def test_update_with_wrong_customer_id_should_fail(customer_repo: CustomerSQLRepository, customer: Customer) -> None:
    customer.id = "wrong id"

    with pytest.raises(ServerError):
        customer_repo.update(customer)


def test_update_with_invalid_country_in_address_should_fail(
    customer_repo: CustomerSQLRepository,
    customer: Customer,
    company_info_with_invalid_country: CompanyInfo,
) -> None:
    customer_repo.create(customer)
    customer.update(
        editor_id=customer.relation_manager_id,
        company_info=company_info_with_invalid_country,
    )

    with pytest.raises(InvalidData):
        customer_repo.update(customer)


def test_update_with_invalid_language_in_contact_person_should_fail(
    customer_repo: CustomerSQLRepository, customer_with_invalid_language: Customer
) -> None:
    customer_repo.create(customer_with_invalid_language)

    with pytest.raises(InvalidData):
        customer_repo.update(customer_with_invalid_language)


def test_create_with_invalid_country_should_fail(
    customer_repo: CustomerSQLRepository, customer_with_invalid_country: Customer
) -> None:
    with pytest.raises(InvalidData):
        customer_repo.create(customer=customer_with_invalid_country)

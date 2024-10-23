from collections.abc import Sequence
from unittest.mock import MagicMock

import pytest

from building_blocks.domain.exceptions import DuplicateEntry, InvalidEmailAddress, InvalidPhoneNumber, ValueNotAllowed
from customer_management.domain.entities.contact_person import ContactPerson, ContactPersonReadOnly
from customer_management.domain.entities.customer import Customer
from customer_management.domain.exceptions import (
    CannotConvertArchivedCustomer,
    ContactPersonAlreadyExists,
    ContactPersonDoesNotExist,
    CustomerAlreadyArchived,
    CustomerAlreadyConverted,
    CustomerStillHasNotClosedOpportunities,
    InvalidCustomerStatus,
    NotEnoughContactPersons,
    NotEnoughPreferredContactMethods,
    OnlyRelationManagerCanChangeStatus,
    OnlyRelationManagerCanModifyCustomerData,
)
from customer_management.domain.services.customer import ensure_all_opportunities_are_closed
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.company_segment import CompanySegment
from customer_management.domain.value_objects.contact_method import ContactMethod
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.customer_status import CustomerStatusName
from customer_management.domain.value_objects.industry import Industry
from customer_management.domain.value_objects.language import Language


@pytest.fixture()
def industry() -> Industry:
    return Industry(name="automotive")


@pytest.fixture()
def segment() -> CompanySegment:
    return CompanySegment(legal_form="limited", size="medium")


@pytest.fixture()
def country() -> Country:
    return Country(code="pl", name="Poland")


@pytest.fixture()
def address() -> Address:
    return Address(
        country=country,
        street="Street",
        street_no="123",
        postal_code="11222",
        city="city",
    )


@pytest.fixture()
def company_info(industry: Industry, segment: CompanySegment, address: Address) -> CompanyInfo:
    return CompanyInfo(name="Company", industry=industry, segment=segment, address=address)


@pytest.fixture()
def company_info_2(industry: Industry, segment: CompanySegment, address: Address) -> CompanyInfo:
    return CompanyInfo(name="Other company", industry=industry, segment=segment, address=address)


@pytest.fixture()
def language() -> Language:
    return Language(code="pl", name="polish")


@pytest.fixture()
def contact_method() -> ContactMethod:
    return ContactMethod(type="email", value="test@example.com", is_preferred=True)


@pytest.fixture()
def contact_person(language: Language, contact_method: ContactMethod) -> ContactPerson:
    return ContactPerson(
        id="cp_1",
        first_name="Jan",
        last_name="Kowalski",
        job_title="CEO",
        preferred_language=language,
        contact_methods=(contact_method,),
    )


@pytest.fixture()
def customer(company_info: CompanyInfo) -> Customer:
    return Customer(id="customer_1", company_info=company_info, relation_manager_id="salesman_1")


@pytest.fixture()
def customer_with_contact_persons(company_info: CompanyInfo, contact_person: ContactPerson) -> Customer:
    customer = Customer(id="customer_2", company_info=company_info, relation_manager_id="salesman_1")
    customer.add_contact_person(
        editor_id=customer.relation_manager_id,
        contact_person_id=contact_person.id,
        first_name=contact_person.first_name,
        last_name=contact_person.last_name,
        job_title=contact_person.job_title,
        preferred_language=contact_person.preferred_language,
        contact_methods=contact_person.contact_methods,
    )
    return customer


def test_industry_creation_with_invalid_name_should_fail() -> None:
    with pytest.raises(ValueNotAllowed):
        Industry(name="invalid industry")


@pytest.mark.parametrize("legal_form,size", [("invalid", "medium"), ("limited", "invalid")])
def test_segment_creation_with_invalid_values_should_fail(legal_form: str, size: str) -> None:
    with pytest.raises(ValueNotAllowed):
        CompanySegment(legal_form=legal_form, size=size)


def test_contact_method_with_invalid_phone_should_fail() -> None:
    with pytest.raises(InvalidPhoneNumber):
        ContactMethod(type="phone", value="invalid phone")


def test_contact_method_with_invalid_email_should_fail() -> None:
    with pytest.raises(InvalidEmailAddress):
        ContactMethod(type="email", value="invalid email")


def test_customer_creation(customer: Customer, company_info: CompanyInfo) -> None:
    assert customer.id == "customer_1"
    assert customer.company_info == company_info
    assert customer.relation_manager_id == "salesman_1"
    assert len(customer.contact_persons) == 0


def test_customer_reconstitution(
    company_info: CompanyInfo,
    contact_person: ContactPerson,
) -> None:
    customer = Customer.reconstitute(
        id="customer_1",
        relation_manager_id="salesman_1",
        company_info=company_info,
        status=CustomerStatusName.INITIAL,
        contact_persons=(contact_person,),
    )
    assert customer.id == "customer_1"
    assert customer.relation_manager_id == "salesman_1"
    assert customer.company_info == company_info
    assert customer.contact_persons[0].id == contact_person.id
    assert customer.status == CustomerStatusName.INITIAL


def test_customer_reconstitution_with_wrong_status_name_should_fail(
    company_info: CompanyInfo,
    contact_person: ContactPerson,
) -> None:
    with pytest.raises(InvalidCustomerStatus):
        Customer.reconstitute(
            id="customer_1",
            relation_manager_id="salesman_1",
            company_info=company_info,
            status="invalid status",
            contact_persons=(contact_person,),
        )


def test_newly_created_customer_should_have_initial_status(customer: Customer) -> None:
    assert customer.status == CustomerStatusName.INITIAL


def test_update_customer(customer: Customer, company_info_2: CompanyInfo) -> None:
    new_relation_manager_id = "new-manager"
    customer.update(
        editor_id=customer.relation_manager_id,
        relation_manager_id=new_relation_manager_id,
        company_info=company_info_2,
    )

    assert customer.relation_manager_id == new_relation_manager_id
    assert customer.company_info == company_info_2


def test_partial_update_customer(customer: Customer, company_info_2: CompanyInfo) -> None:
    old_relation_manager_id = customer.relation_manager_id
    customer.update(editor_id=old_relation_manager_id, company_info=company_info_2)

    assert customer.relation_manager_id == old_relation_manager_id
    assert customer.company_info == company_info_2


def test_update_by_non_relation_manager_should_fail(customer: Customer) -> None:
    with pytest.raises(OnlyRelationManagerCanModifyCustomerData):
        customer.update(editor_id="non relation manager", relation_manager_id="new-id")


def test_convert_customer_by_non_relation_manager_should_fail(
    customer: Customer,
) -> None:
    with pytest.raises(OnlyRelationManagerCanChangeStatus):
        customer.convert("salesman_2")


def test_archive_customer_by_non_relation_manager_should_fail(
    customer: Customer,
) -> None:
    with pytest.raises(OnlyRelationManagerCanChangeStatus):
        customer.archive("salesman_2")


def test_convert_customer_with_no_contact_persons_should_fail(
    customer: Customer,
) -> None:
    with pytest.raises(NotEnoughContactPersons):
        customer.convert(customer.relation_manager_id)


def test_convert_customer_should_change_status_to_converted(
    customer_with_contact_persons: Customer,
) -> None:
    customer_with_contact_persons.convert(customer_with_contact_persons.relation_manager_id)

    assert customer_with_contact_persons.status == CustomerStatusName.CONVERTED


def test_convert_already_converted_customer_should_fail(
    customer_with_contact_persons: Customer,
) -> None:
    customer_with_contact_persons.convert(customer_with_contact_persons.relation_manager_id)

    with pytest.raises(CustomerAlreadyConverted):
        customer_with_contact_persons.convert(customer_with_contact_persons.relation_manager_id)


def test_convert_archived_customer_should_fail(
    customer_with_contact_persons: Customer,
) -> None:
    manager_id = customer_with_contact_persons.relation_manager_id
    customer_with_contact_persons.convert(manager_id)
    customer_with_contact_persons.archive(manager_id)

    with pytest.raises(CannotConvertArchivedCustomer):
        customer_with_contact_persons.convert(manager_id)


def test_archive_customer_should_change_status_to_archived(customer: Customer) -> None:
    customer.archive(customer.relation_manager_id)

    assert customer.status == CustomerStatusName.ARCHIVED


def test_archive_already_archived_customer_should_fail(customer: Customer) -> None:
    customer.archive(customer.relation_manager_id)

    with pytest.raises(CustomerAlreadyArchived):
        customer.archive(customer.relation_manager_id)


def test_get_contact_person(customer_with_contact_persons: Customer, contact_person: ContactPerson) -> None:
    retrieved_person = customer_with_contact_persons.get_contact_person(contact_person.id)

    assert retrieved_person.id == contact_person.id


def test_get_contact_person_with_wrong_id_should_fail(
    customer_with_contact_persons: Customer,
) -> None:
    with pytest.raises(ContactPersonDoesNotExist):
        customer_with_contact_persons.get_contact_person("invalid id")


def test_returned_contact_persons_are_read_only(
    customer_with_contact_persons: Customer,
) -> None:
    assert isinstance(customer_with_contact_persons.contact_persons[0], ContactPersonReadOnly)


def test_add_contact_person(customer_with_contact_persons: Customer, contact_person: ContactPerson) -> None:
    assert customer_with_contact_persons.contact_persons[0].id == contact_person.id


def test_add_contact_person_with_existing_id_should_fail(
    customer_with_contact_persons: Customer, contact_person: ContactPerson
) -> None:
    with pytest.raises(ContactPersonAlreadyExists):
        customer_with_contact_persons.add_contact_person(
            editor_id=customer_with_contact_persons.relation_manager_id,
            contact_person_id=contact_person.id,
            first_name=contact_person.first_name,
            last_name=contact_person.last_name,
            contact_methods=contact_person.contact_methods,
            job_title="irrelevant",
            preferred_language=contact_person.preferred_language,
        )


def test_add_contact_person_with_duplicates_should_fail(
    customer_with_contact_persons: Customer, contact_person: ContactPerson
) -> None:
    with pytest.raises(DuplicateEntry):
        customer_with_contact_persons.add_contact_person(
            editor_id=customer_with_contact_persons.relation_manager_id,
            contact_person_id="cp_2",
            first_name=contact_person.first_name,
            last_name=contact_person.last_name,
            contact_methods=contact_person.contact_methods,
            job_title="irrelevant",
            preferred_language=contact_person.preferred_language,
        )


def test_add_contact_person_without_preferred_contact_method_should_fail(
    customer: Customer, language: Language
) -> None:
    contact_method = ContactMethod(type="email", value="email@example.com")
    with pytest.raises(NotEnoughPreferredContactMethods):
        customer.add_contact_person(
            editor_id=customer.relation_manager_id,
            contact_person_id="cp_1",
            first_name="Jan",
            last_name="Kowalski",
            job_title="CEO",
            preferred_language=language,
            contact_methods=(contact_method,),
        )


def test_update_contact_person(customer_with_contact_persons: Customer, contact_person: ContactPerson) -> None:
    language = Language(code="en", name="english")
    contact_method = ContactMethod(type="email", value="test2@example.com", is_preferred=True)

    customer_with_contact_persons.update_contact_person(
        editor_id=customer_with_contact_persons.relation_manager_id,
        contact_person_id=contact_person.id,
        first_name="Paweł",
        last_name="Kowalczyk",
        job_title="CFO",
        preferred_language=language,
        contact_methods=(contact_method,),
    )
    person = customer_with_contact_persons.get_contact_person(contact_person.id)

    assert person.first_name == "Paweł"
    assert person.last_name == "Kowalczyk"
    assert person.job_title == "CFO"
    assert person.preferred_language == language
    assert person.contact_methods == (contact_method,)


def test_update_contact_person_partial_update(
    customer_with_contact_persons: Customer, contact_person: ContactPerson
) -> None:
    customer_with_contact_persons.update_contact_person(
        editor_id=customer_with_contact_persons.relation_manager_id,
        contact_person_id=contact_person.id,
        first_name="Paweł",
    )
    person = customer_with_contact_persons.get_contact_person(contact_person.id)

    assert person.first_name == "Paweł"
    assert person.last_name == contact_person.last_name
    assert person.job_title == contact_person.job_title
    assert person.preferred_language == contact_person.preferred_language
    assert person.contact_methods == contact_person.contact_methods


def test_update_contact_person_with_wrong_id_should_fail(
    customer_with_contact_persons: Customer,
) -> None:
    with pytest.raises(ContactPersonDoesNotExist):
        customer_with_contact_persons.update_contact_person(
            editor_id=customer_with_contact_persons.relation_manager_id,
            contact_person_id="invalid id",
        )


def test_update_contact_person_with_duplicates_should_fail(
    customer_with_contact_persons: Customer,
    contact_person: ContactPerson,
    contact_method: ContactMethod,
    language: Language,
) -> None:
    customer_with_contact_persons.add_contact_person(
        editor_id=customer_with_contact_persons.relation_manager_id,
        contact_person_id="cp_2",
        first_name="Piotr",
        last_name="Nowak",
        job_title="CEO",
        preferred_language=language,
        contact_methods=(contact_method,),
    )

    with pytest.raises(DuplicateEntry):
        customer_with_contact_persons.update_contact_person(
            editor_id=customer_with_contact_persons.relation_manager_id,
            contact_person_id="cp_2",
            first_name=contact_person.first_name,
            last_name=contact_person.last_name,
            contact_methods=contact_person.contact_methods,
        )


@pytest.mark.parametrize("method_name", ["add_contact_person", "update_contact_person"])
def test_create_or_update_contact_person_by_non_relation_manager_should_fail(
    customer_with_contact_persons: Customer,
    language: Language,
    contact_method: ContactMethod,
    method_name: str,
) -> None:
    with pytest.raises(OnlyRelationManagerCanModifyCustomerData):
        getattr(customer_with_contact_persons, method_name)(
            editor_id="non-manager",
            contact_person_id="cp-id",
            first_name="Jan",
            last_name="Kowalski",
            job_title="COO",
            preferred_language=language,
            contact_methods=[contact_method],
        )


def test_remove_contact_person(customer_with_contact_persons: Customer) -> None:
    person_id = customer_with_contact_persons.contact_persons[0].id
    customer_with_contact_persons.remove_contact_person(
        id_to_remove=person_id,
        editor_id=customer_with_contact_persons.relation_manager_id,
    )

    assert len(customer_with_contact_persons.contact_persons) == 0


def test_remove_contact_person_with_wrong_id_should_fail(
    customer_with_contact_persons: Customer,
) -> None:
    with pytest.raises(ContactPersonDoesNotExist):
        customer_with_contact_persons.remove_contact_person(
            id_to_remove="invalid id",
            editor_id=customer_with_contact_persons.relation_manager_id,
        )


def test_remove_contact_person_by_non_relation_manager_should_fail(
    customer_with_contact_persons: Customer,
) -> None:
    person_id = customer_with_contact_persons.contact_persons[0].id
    with pytest.raises(OnlyRelationManagerCanModifyCustomerData):
        customer_with_contact_persons.remove_contact_person(editor_id="non manager", id_to_remove=person_id)


@pytest.mark.parametrize(
    "opportunities",
    [
        tuple(),
        (MagicMock(stage_name="closed-won"), MagicMock(stage_name="closed-lost")),
    ],
)
def test_ensure_all_opportunities_are_closed_should_not_fail_if_does_not_have_open_opportunities(
    opportunities: Sequence,
) -> None:
    ensure_all_opportunities_are_closed(opportunities)


@pytest.mark.parametrize(
    "opportunities",
    [
        (MagicMock(stage_name="closed-won"), MagicMock(stage_name="other")),
        (MagicMock(stage_name="other"),),
    ],
)
def test_ensure_all_opportunities_are_closed_should_fail_if_has_open_opportunities(
    opportunities: Sequence,
) -> None:
    with pytest.raises(CustomerStillHasNotClosedOpportunities):
        ensure_all_opportunities_are_closed(opportunities)

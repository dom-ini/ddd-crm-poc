from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import ConfictingAction, InvalidData, ObjectDoesNotExist, UnauthorizedAction
from building_blocks.domain.exceptions import DomainException, DuplicateEntry
from customer_management.application.command import CustomerCommandUseCase, CustomerUnitOfWork
from customer_management.application.command_model import (
    AddressDataCreateUpdateModel,
    CompanyInfoCreateUpdateModel,
    ContactMethodCreateUpdateModel,
    ContactPersonCreateModel,
    ContactPersonUpdateModel,
    CountryCreateUpdateModel,
    CustomerCreateModel,
    CustomerUpdateModel,
    LanguageCreateUpdateModel,
)
from customer_management.domain.entities.customer.customer import Customer
from customer_management.domain.exceptions import (
    CannotConvertArchivedCustomer,
    ContactPersonDoesNotExist,
    CustomerAlreadyArchived,
    CustomerAlreadyConverted,
    NotEnoughContactPersons,
    NotEnoughPreferredContactMethods,
    OnlyRelationManagerCanChangeStatus,
    OnlyRelationManagerCanModifyCustomerData,
)
from customer_management.domain.repositories.customer import CustomerRepository

address_example = AddressDataCreateUpdateModel(
    country=CountryCreateUpdateModel(code="pl", name="Polska"),
    street="Ulica",
    street_no="123",
    postal_code="11-222",
    city="Miasto",
)
language_example = LanguageCreateUpdateModel(name="polski", code="pl")
valid_contact_method_example = ContactMethodCreateUpdateModel(type="email", value="test@example.com", is_preferred=True)
invalid_contact_method_example = ContactMethodCreateUpdateModel(type="phone", value="invalid", is_preferred=False)


@pytest.fixture()
def mock_customer_repository() -> CustomerRepository:
    repository = MagicMock(spec=CustomerRepository)
    return repository


@pytest.fixture()
def customer_uow(mock_customer_repository: CustomerRepository) -> CustomerUnitOfWork:
    uow = MagicMock(spec=CustomerUnitOfWork)
    uow.repository = mock_customer_repository
    return uow


@pytest.fixture()
def customer_command_use_case(
    customer_uow: CustomerUnitOfWork,
) -> CustomerCommandUseCase:
    return CustomerCommandUseCase(customer_uow=customer_uow)


@pytest.fixture()
def mock_customer() -> MagicMock:
    return MagicMock(spec=Customer)


@pytest.mark.parametrize(
    "data",
    [
        CustomerCreateModel(
            relation_manager_id="salesman-1",
            company_info=CompanyInfoCreateUpdateModel(
                name="company name",
                industry="invalid industry",
                size="medium",
                legal_form="limited",
                address=address_example,
            ),
        ),
        CustomerCreateModel(
            relation_manager_id="salesman-1",
            company_info=CompanyInfoCreateUpdateModel(
                name="company name",
                industry="automotive",
                size="invalid size",
                legal_form="limited",
                address=address_example,
            ),
        ),
        CustomerCreateModel(
            relation_manager_id="salesman-1",
            company_info=CompanyInfoCreateUpdateModel(
                name="company name",
                industry="automotive",
                size="medium",
                legal_form="invalid legal form",
                address=address_example,
            ),
        ),
    ],
)
def test_create_customer_correctly_raises_invalid_data(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    data: CustomerCreateModel,
) -> None:
    with pytest.raises(InvalidData):
        customer_command_use_case.create(customer_data=data)

    customer_uow.__enter__().repository.create.assert_not_called()


@pytest.mark.parametrize(
    "data",
    [
        CustomerUpdateModel(
            relation_manager_id="salesman-1",
            company_info=CompanyInfoCreateUpdateModel(
                name="company name",
                industry="invalid industry",
                size="medium",
                legal_form="limited",
                address=address_example,
            ),
        ),
        CustomerUpdateModel(
            relation_manager_id="salesman-1",
            company_info=CompanyInfoCreateUpdateModel(
                name="company name",
                industry="automotive",
                size="invalid size",
                legal_form="limited",
                address=address_example,
            ),
        ),
        CustomerUpdateModel(
            relation_manager_id="salesman-1",
            company_info=CompanyInfoCreateUpdateModel(
                name="company name",
                industry="automotive",
                size="medium",
                legal_form="invalid legal form",
                address=address_example,
            ),
        ),
    ],
)
def test_update_customer_correctly_raises_invalid_data(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    data: CustomerUpdateModel,
) -> None:
    with pytest.raises(InvalidData):
        customer_command_use_case.update(customer_id="customer-1", editor_id="salesman-1", customer_data=data)

    customer_uow.__enter__().repository.update.assert_not_called()


@pytest.mark.parametrize(
    "data,causing_exc_class",
    [
        (
            ContactPersonCreateModel(
                first_name="Jan",
                last_name="Kowalski",
                job_title="CEO",
                preferred_language=language_example,
                contact_methods=[invalid_contact_method_example],
            ),
            None,
        ),
        (
            ContactPersonCreateModel(
                first_name="Jan",
                last_name="Kowalski",
                job_title="CEO",
                preferred_language=language_example,
                contact_methods=[valid_contact_method_example],
            ),
            NotEnoughPreferredContactMethods,
        ),
        (
            ContactPersonCreateModel(
                first_name="Jan",
                last_name="Kowalski",
                job_title="CEO",
                preferred_language=language_example,
                contact_methods=[valid_contact_method_example],
            ),
            DuplicateEntry([]),
        ),
    ],
)
def test_create_contact_person_correctly_raises_invalid_data(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    mock_customer: MagicMock,
    data: ContactPersonCreateModel,
    causing_exc_class: type[DomainException],
) -> None:
    customer_uow.__enter__().repository.get.return_value = mock_customer
    mock_customer.add_contact_person.side_effect = causing_exc_class

    with pytest.raises(InvalidData):
        customer_command_use_case.create_contact_person(customer_id="customer", editor_id="salesman-1", data=data)


@pytest.mark.parametrize(
    "data,causing_exc_class",
    [
        (
            ContactPersonUpdateModel(
                first_name="Jan",
                last_name="Kowalski",
                job_title="CEO",
                preferred_language=language_example,
                contact_methods=[invalid_contact_method_example],
            ),
            None,
        ),
        (
            ContactPersonUpdateModel(
                first_name="Jan",
                last_name="Kowalski",
                job_title="CEO",
                preferred_language=language_example,
                contact_methods=[valid_contact_method_example],
            ),
            NotEnoughPreferredContactMethods,
        ),
        (
            ContactPersonUpdateModel(
                first_name="Jan",
                last_name="Kowalski",
                job_title="CEO",
                preferred_language=language_example,
                contact_methods=[valid_contact_method_example],
            ),
            DuplicateEntry([]),
        ),
    ],
)
def test_update_contact_person_correctly_raises_invalid_data(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    mock_customer: MagicMock,
    data: ContactPersonUpdateModel,
    causing_exc_class: type[DomainException],
) -> None:
    customer_uow.__enter__().repository.get.return_value = mock_customer
    mock_customer.update_contact_person.side_effect = causing_exc_class

    with pytest.raises(InvalidData):
        customer_command_use_case.update_contact_person(
            customer_id="customer",
            contact_person_id="cp-1",
            editor_id="salesman-1",
            data=data,
        )


@pytest.mark.parametrize(
    "method_name,domain_method_name,kwargs",
    [
        (
            "update",
            "update",
            {"customer_data": CustomerUpdateModel(relation_manager_id="salesman-1")},
        ),
        (
            "create_contact_person",
            "add_contact_person",
            {
                "data": ContactPersonCreateModel(
                    first_name="Jan",
                    last_name="Kowalski",
                    job_title="CEO",
                    preferred_language=language_example,
                    contact_methods=[valid_contact_method_example],
                )
            },
        ),
        (
            "update_contact_person",
            "update_contact_person",
            {
                "contact_person_id": "cp-1",
                "data": ContactPersonUpdateModel(first_name="Jan"),
            },
        ),
        (
            "remove_contact_person",
            "remove_contact_person",
            {
                "contact_person_id": "cp-1",
            },
        ),
    ],
)
def test_calling_methods_by_unauthorized_user_should_fail(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    mock_customer: MagicMock,
    method_name: str,
    domain_method_name: str,
    kwargs: dict,
) -> None:
    customer_uow.__enter__().repository.get.return_value = mock_customer
    getattr(mock_customer, domain_method_name).side_effect = OnlyRelationManagerCanModifyCustomerData

    with pytest.raises(UnauthorizedAction):
        getattr(customer_command_use_case, method_name)(customer_id="customer-1", editor_id="salesman-1", **kwargs)


@pytest.mark.parametrize(
    "method_name,kwargs",
    [
        (
            "update",
            {"customer_data": CustomerUpdateModel(relation_manager_id="salesman-1")},
        ),
        (
            "create_contact_person",
            {
                "data": ContactPersonCreateModel(
                    first_name="Jan",
                    last_name="Kowalski",
                    job_title="CEO",
                    preferred_language=language_example,
                    contact_methods=[valid_contact_method_example],
                )
            },
        ),
        (
            "update_contact_person",
            {
                "contact_person_id": "cp-1",
                "data": ContactPersonUpdateModel(first_name="Jan"),
            },
        ),
        (
            "remove_contact_person",
            {
                "contact_person_id": "cp-1",
            },
        ),
    ],
)
def test_calling_methods_with_wrong_customer_id_should_fail(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    method_name: str,
    kwargs: dict,
) -> None:
    customer_uow.__enter__().repository.get.return_value = None

    with pytest.raises(ObjectDoesNotExist):
        getattr(customer_command_use_case, method_name)(customer_id="customer-1", editor_id="salesman-1", **kwargs)

    customer_uow.__enter__().repository.update.assert_not_called()


def test_remove_contact_person_with_wrong_person_id_should_fail(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    mock_customer: MagicMock,
) -> None:
    customer_uow.__enter__().repository.get.return_value = mock_customer
    mock_customer.remove_contact_person.side_effect = ContactPersonDoesNotExist

    with pytest.raises(ObjectDoesNotExist):
        customer_command_use_case.remove_contact_person(
            customer_id="customer-1", editor_id="salesman-1", contact_person_id="cp-1"
        )


def test_convert_correctly_raises_invalid_data(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    mock_customer: MagicMock,
) -> None:
    customer_uow.__enter__().repository.get.return_value = mock_customer
    mock_customer.convert.side_effect = NotEnoughContactPersons

    with pytest.raises(InvalidData):
        customer_command_use_case.convert(customer_id="customer-1", requestor_id="salesman-1")


@pytest.mark.parametrize(
    "method_name,exception",
    [
        ("convert", CustomerAlreadyConverted),
        ("convert", CannotConvertArchivedCustomer),
        ("archive", CustomerAlreadyArchived),
    ],
)
def test_convert_or_archive_correctly_raises_conflicting_action(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    mock_customer: MagicMock,
    method_name: str,
    exception: type[DomainException],
) -> None:
    customer_uow.__enter__().repository.get.return_value = mock_customer
    getattr(mock_customer, method_name).side_effect = exception

    with pytest.raises(ConfictingAction):
        getattr(customer_command_use_case, method_name)(customer_id="customer-1", requestor_id="salesman-1")


@pytest.mark.parametrize("method_name", ["convert", "archive"])
def test_convert_or_archive_by_non_relation_manager_should_fail(
    customer_uow: CustomerUnitOfWork,
    customer_command_use_case: CustomerCommandUseCase,
    mock_customer: MagicMock,
    method_name: str,
) -> None:
    customer_uow.__enter__().repository.get.return_value = mock_customer
    getattr(mock_customer, method_name).side_effect = OnlyRelationManagerCanChangeStatus

    with pytest.raises(UnauthorizedAction):
        getattr(customer_command_use_case, method_name)(customer_id="customer-1", requestor_id="salesman-1")

from collections.abc import Iterable
from uuid import uuid4
from building_blocks.application.command import BaseUnitOfWork
from customer_management.domain.repositories.customer import CustomerRepository
from customer_management.application.command_model import (
    AddressDataCreateUpdateModel,
    CompanyInfoCreateUpdateModel,
    ContactMethodCreateUpdateModel,
    ContactPersonCreateModel,
    ContactPersonUpdateModel,
    CustomerCreateModel,
    CustomerUpdateModel,
    LanguageCreateUpdateModel,
)
from customer_management.application.query_model import (
    ContactPersonReadModel,
    CustomerReadModel,
)
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.address import Address
from customer_management.domain.entities.customer.customer import Customer
from customer_management.domain.value_objects.company_segment import CompanySegment
from customer_management.domain.value_objects.industry import Industry
from building_blocks.domain.exceptions import (
    DuplicateEntry,
    InvalidEmailAddress,
    InvalidPhoneNumber,
    ValueNotAllowed,
)
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.contact_method import ContactMethod
from customer_management.domain.value_objects.language import Language
from customer_management.domain.exceptions import (
    CannotConvertArchivedCustomer,
    ContactPersonDoesNotExist,
    CustomerAlreadyArchived,
    CustomerAlreadyConverted,
    NotEnoughContactPersons,
    NotEnoughPreferredContactMethods,
    OnlyRelationManagerCanChangeStatus,
)
from building_blocks.application.exceptions import (
    InvalidData,
    ObjectDoesNotExist,
    UnauthorizedAction,
)


class CustomerUnitOfWork(BaseUnitOfWork):
    repository: CustomerRepository


class CustomerCommandUseCase:
    def __init__(self, customer_uow: CustomerUnitOfWork) -> None:
        self.customer_uow = customer_uow

    def create(self, customer_data: CustomerCreateModel) -> CustomerReadModel:
        customer_id = str(uuid4())
        company_info = self._create_company_info(customer_data.company_info)
        customer = Customer(
            id=customer_id,
            company_info=company_info,
            relation_manager_id=customer_data.relation_manager_id,
        )
        with self.customer_uow as uow:
            uow.repository.create(customer)
        return CustomerReadModel.from_domain(customer)

    def update(
        self, customer_id: str, customer_data: CustomerUpdateModel
    ) -> CustomerReadModel:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            if customer_data.relation_manager_id is not None:
                customer.change_relation_manager(customer_data.relation_manager_id)
            if customer_data.company_info is not None:
                customer.company_info = self._create_company_info(
                    customer_data.company_info
                )
            uow.repository.update(customer)
        return CustomerReadModel.from_domain(customer)

    def convert(self, customer_id: str, requestor_id: str) -> None:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                customer.convert(requestor_id)
            except (
                OnlyRelationManagerCanChangeStatus,
                CustomerAlreadyConverted,
                CannotConvertArchivedCustomer,
            ) as e:
                raise UnauthorizedAction(e.message)
            except NotEnoughContactPersons as e:
                raise InvalidData(e.message)
            uow.repository.update(customer)

    def archive(self, customer_id: str, requestor_id: str) -> None:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                customer.archive(requestor_id)
            except (
                OnlyRelationManagerCanChangeStatus,
                CustomerAlreadyArchived,
            ) as e:
                raise UnauthorizedAction(e.message)
            uow.repository.update(customer)

    def create_contact_person(
        self, customer_id: str, data: ContactPersonCreateModel
    ) -> ContactPersonReadModel:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            contact_person_id = str(uuid4())
            language = self._create_preferred_language(data.preferred_language)
            contact_methods = self._create_contact_methods(data.contact_methods)
            try:
                customer.add_contact_person(
                    contact_person_id=contact_person_id,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    job_title=data.job_title,
                    preferred_language=language,
                    contact_methods=contact_methods,
                )
            except (NotEnoughPreferredContactMethods, DuplicateEntry) as e:
                raise InvalidData(e.message)
            uow.repository.update(customer)
        contact_person = customer.get_contact_person(contact_person_id)
        return ContactPersonReadModel.from_domain(contact_person)

    def update_contact_person(
        self, customer_id: str, contact_person_id: str, data: ContactPersonUpdateModel
    ) -> ContactPersonReadModel:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                language = (
                    self._create_preferred_language(data.preferred_language)
                    if data.preferred_language
                    else None
                )
                contact_methods = (
                    self._create_contact_methods(data.contact_methods)
                    if data.contact_methods
                    else None
                )
                customer.update_contact_person(
                    contact_person_id=contact_person_id,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    job_title=data.job_title,
                    preferred_language=language,
                    contact_methods=contact_methods,
                )
            except ContactPersonDoesNotExist:
                raise ObjectDoesNotExist(contact_person_id)
            except (NotEnoughPreferredContactMethods, DuplicateEntry) as e:
                raise InvalidData(e.message)
            uow.repository.update(customer)
        contact_person = customer.get_contact_person(contact_person_id)
        return ContactPersonReadModel.from_domain(contact_person)

    def remove_contact_person(self, customer_id: str, contact_person_id: str) -> None:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                customer.remove_contact_person(contact_person_id)
            except ContactPersonDoesNotExist:
                raise ObjectDoesNotExist(customer_id)
            uow.repository.update(customer)

    def _get_customer(self, uow: CustomerUnitOfWork, customer_id: str) -> Customer:
        customer = uow.repository.get(customer_id)
        if customer is None:
            raise ObjectDoesNotExist(customer_id)
        return customer

    def _create_preferred_language(self, data: LanguageCreateUpdateModel) -> Language:
        language = Language(code=data.code, name=data.name)
        return language

    def _create_single_contact_method(
        self, data: ContactMethodCreateUpdateModel
    ) -> ContactMethod:
        try:
            contact_method = ContactMethod(
                type=data.type,
                value=data.value,
                is_preferred=data.is_preferred,
            )
        except (InvalidPhoneNumber, InvalidEmailAddress) as e:
            raise InvalidData(e.message)
        return contact_method

    def _create_contact_methods(
        self, data: Iterable[ContactMethodCreateUpdateModel]
    ) -> Iterable[ContactMethod]:
        contact_methods = tuple(
            self._create_single_contact_method(method) for method in data
        )
        return contact_methods

    def _create_company_info(
        self, company_data: CompanyInfoCreateUpdateModel
    ) -> CompanyInfo:
        address = self._create_address(company_data.address)
        try:
            industry = Industry(name=company_data.industry)
            segment = CompanySegment(
                size=company_data.size, legal_form=company_data.legal_form
            )
            company_info = CompanyInfo(
                name=company_data.name,
                industry=industry,
                segment=segment,
                address=address,
            )
        except ValueNotAllowed as e:
            raise InvalidData(e.message)
        return company_info

    def _create_address(self, address_data: AddressDataCreateUpdateModel) -> Address:
        country = Country(
            code=address_data.country.code, name=address_data.country.name
        )
        address = Address(
            country=country,
            street=address_data.street,
            street_no=address_data.street_no,
            postal_code=address_data.postal_code,
            city=address_data.city,
        )
        return address

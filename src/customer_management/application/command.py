from collections.abc import Iterable
from uuid import uuid4

from building_blocks.application.command import BaseUnitOfWork
from building_blocks.application.exceptions import ConflictingAction, ForbiddenAction, InvalidData, ObjectDoesNotExist
from building_blocks.domain.exceptions import DuplicateEntry, InvalidEmailAddress, InvalidPhoneNumber, ValueNotAllowed
from customer_management.application.acl import IOpportunityService, ISalesRepresentativeService
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
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.domain.entities.customer import Customer
from customer_management.domain.exceptions import (
    CannotConvertArchivedCustomer,
    ContactPersonDoesNotExist,
    CustomerAlreadyArchived,
    CustomerAlreadyConverted,
    CustomerStillHasNotClosedOpportunities,
    NotEnoughContactPersons,
    NotEnoughPreferredContactMethods,
    OnlyRelationManagerCanChangeStatus,
    OnlyRelationManagerCanModifyCustomerData,
)
from customer_management.domain.repositories.customer import CustomerRepository
from customer_management.domain.services.customer import ensure_all_opportunities_are_closed
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.company_segment import CompanySegment
from customer_management.domain.value_objects.contact_method import ContactMethod
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.industry import Industry
from customer_management.domain.value_objects.language import Language


class CustomerUnitOfWork(BaseUnitOfWork):
    repository: CustomerRepository


class CustomerCommandUseCase:
    def __init__(
        self,
        customer_uow: CustomerUnitOfWork,
        sales_rep_service: ISalesRepresentativeService,
        opportunity_service: IOpportunityService,
    ) -> None:
        self.customer_uow = customer_uow
        self.sales_rep_service = sales_rep_service
        self.opportunity_service = opportunity_service

    def create(self, customer_data: CustomerCreateModel) -> CustomerReadModel:
        self._verify_that_salesman_exists(customer_data.relation_manager_id)

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

    def update(self, customer_id: str, editor_id: str, customer_data: CustomerUpdateModel) -> CustomerReadModel:
        self._verify_that_salesman_exists(customer_data.relation_manager_id)

        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                customer.update(
                    editor_id=editor_id,
                    relation_manager_id=customer_data.relation_manager_id,
                    company_info=self._create_company_info_if_provided(customer_data.company_info),
                )
            except OnlyRelationManagerCanModifyCustomerData as e:
                raise ForbiddenAction(e.message) from e
            uow.repository.update(customer)
        return CustomerReadModel.from_domain(customer)

    def convert(self, customer_id: str, requestor_id: str) -> None:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                customer.convert(requestor_id)
            except (
                CustomerAlreadyConverted,
                CannotConvertArchivedCustomer,
            ) as e:
                raise ConflictingAction(e.message) from e
            except (OnlyRelationManagerCanChangeStatus,) as e:
                raise ForbiddenAction(e.message) from e
            except NotEnoughContactPersons as e:
                raise InvalidData(e.message) from e
            uow.repository.update(customer)

    def archive(self, customer_id: str, requestor_id: str) -> None:
        self._enforce_archive_business_rules(customer_id=customer_id)

        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                customer.archive(requestor_id)
            except (CustomerAlreadyArchived,) as e:
                raise ConflictingAction(e.message) from e
            except (OnlyRelationManagerCanChangeStatus,) as e:
                raise ForbiddenAction(e.message) from e
            uow.repository.update(customer)

    def create_contact_person(
        self, customer_id: str, editor_id: str, data: ContactPersonCreateModel
    ) -> ContactPersonReadModel:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            contact_person_id = str(uuid4())
            language = self._create_preferred_language(data.preferred_language)
            contact_methods = self._create_contact_methods(data.contact_methods)
            try:
                customer.add_contact_person(
                    editor_id=editor_id,
                    contact_person_id=contact_person_id,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    job_title=data.job_title,
                    preferred_language=language,
                    contact_methods=contact_methods,
                )
            except (NotEnoughPreferredContactMethods, DuplicateEntry) as e:
                raise InvalidData(e.message) from e
            except OnlyRelationManagerCanModifyCustomerData as e:
                raise ForbiddenAction(e.message) from e
            uow.repository.update(customer)
        contact_person = customer.get_contact_person(contact_person_id)
        return ContactPersonReadModel.from_domain(contact_person)

    def update_contact_person(
        self,
        customer_id: str,
        contact_person_id: str,
        editor_id: str,
        data: ContactPersonUpdateModel,
    ) -> ContactPersonReadModel:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                language = self._create_preferred_language(data.preferred_language) if data.preferred_language else None
                contact_methods = self._create_contact_methods(data.contact_methods) if data.contact_methods else None
                customer.update_contact_person(
                    editor_id=editor_id,
                    contact_person_id=contact_person_id,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    job_title=data.job_title,
                    preferred_language=language,
                    contact_methods=contact_methods,
                )
            except ContactPersonDoesNotExist as e:
                raise ObjectDoesNotExist(contact_person_id) from e
            except (NotEnoughPreferredContactMethods, DuplicateEntry) as e:
                raise InvalidData(e.message) from e
            except OnlyRelationManagerCanModifyCustomerData as e:
                raise ForbiddenAction(e.message) from e
            uow.repository.update(customer)
        contact_person = customer.get_contact_person(contact_person_id)
        return ContactPersonReadModel.from_domain(contact_person)

    def remove_contact_person(self, customer_id: str, editor_id: str, contact_person_id: str) -> None:
        with self.customer_uow as uow:
            customer = self._get_customer(uow=uow, customer_id=customer_id)
            try:
                customer.remove_contact_person(editor_id=editor_id, id_to_remove=contact_person_id)
            except ContactPersonDoesNotExist as e:
                raise ObjectDoesNotExist(contact_person_id) from e
            except OnlyRelationManagerCanModifyCustomerData as e:
                raise ForbiddenAction(e.message) from e
            uow.repository.update(customer)

    def _get_customer(self, uow: CustomerUnitOfWork, customer_id: str) -> Customer:
        customer = uow.repository.get(customer_id)
        if customer is None:
            raise ObjectDoesNotExist(customer_id)
        return customer

    def _enforce_archive_business_rules(self, customer_id: str) -> None:
        opportunities = self.opportunity_service.get_opportunities_by_customer(customer_id=customer_id)
        try:
            ensure_all_opportunities_are_closed(opportunities)
        except CustomerStillHasNotClosedOpportunities as e:
            raise InvalidData(e.message) from e

    def _verify_that_salesman_exists(self, salesman_id: str) -> None:
        if not self.sales_rep_service.salesman_exists(salesman_id):
            raise InvalidData(f"Relation manager with id={salesman_id} does not exist")

    def _create_company_info_if_provided(self, company_info: CompanyInfoCreateUpdateModel) -> CompanyInfo | None:
        return self._create_company_info(company_info) if company_info else None

    def _create_preferred_language(self, data: LanguageCreateUpdateModel) -> Language:
        language = Language(code=data.code, name=data.name)
        return language

    def _create_single_contact_method(self, data: ContactMethodCreateUpdateModel) -> ContactMethod:
        try:
            contact_method = ContactMethod(
                type=data.type,
                value=data.value,
                is_preferred=data.is_preferred,
            )
        except (InvalidPhoneNumber, InvalidEmailAddress) as e:
            raise InvalidData(e.message) from e
        return contact_method

    def _create_contact_methods(self, data: Iterable[ContactMethodCreateUpdateModel]) -> Iterable[ContactMethod]:
        contact_methods = tuple(self._create_single_contact_method(method) for method in data)
        return contact_methods

    def _create_company_info(self, company_data: CompanyInfoCreateUpdateModel) -> CompanyInfo:
        address = self._create_address(company_data.address)
        try:
            industry = Industry(name=company_data.industry)
            segment = CompanySegment(size=company_data.size, legal_form=company_data.legal_form)
            company_info = CompanyInfo(
                name=company_data.name,
                industry=industry,
                segment=segment,
                address=address,
            )
        except ValueNotAllowed as e:
            raise InvalidData(e.message) from e
        return company_info

    def _create_address(self, address_data: AddressDataCreateUpdateModel) -> Address:
        country = Country(code=address_data.country.code, name=address_data.country.name)
        address = Address(
            country=country,
            street=address_data.street,
            street_no=address_data.street_no,
            postal_code=address_data.postal_code,
            city=address_data.city,
        )
        return address

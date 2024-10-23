from collections.abc import Iterable

from attrs import define
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from building_blocks.application.exceptions import InvalidData
from building_blocks.infrastructure.exceptions import ObjectAlreadyExists, ServerError
from customer_management.domain.entities.contact_person.contact_person import ContactMethods
from customer_management.domain.entities.customer.customer import ContactPersonsReadOnly, Customer
from customer_management.domain.repositories.customer import CustomerRepository
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.infrastructure.sql.customer.models import (
    AddressModel,
    CompanyDataModel,
    ContactMethodModel,
    ContactPersonModel,
    CountryModel,
    CustomerModel,
    LanguageModel,
)


@define
class ContactPersonDbData:
    personal_info: type[ContactPersonModel]
    contact_methods: Iterable[type[ContactMethodModel]]


class CustomerSQLRepository(CustomerRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, customer_id: str) -> Customer | None:
        query = select(CustomerModel).where(CustomerModel.id == customer_id)
        customer = self.db.scalar(query)
        if not customer:
            return None
        return customer.to_domain()

    def create(self, customer: Customer) -> None:
        address_in_db = self._create_address(address=customer.company_info.address)
        self.db.add(address_in_db)
        self.db.flush()

        customer_in_db = CustomerModel.from_domain(customer)
        company_data_in_db = self._create_company_data(
            company_data=customer.company_info,
            address_id=address_in_db.id,
            customer_id=customer.id,
        )
        try:
            self.db.add_all([customer_in_db, company_data_in_db])
        except IntegrityError as e:
            raise ObjectAlreadyExists(f"Customer with id={customer.id} already exists") from e

    def update(self, customer: Customer) -> None:
        updated_customer = CustomerModel.from_domain(entity=customer)
        self.db.merge(updated_customer)

        self._update_company_data(company_data=customer.company_info, customer_id=customer.id)
        self._update_contact_persons(contact_persons=customer.contact_persons, customer_id=customer.id)

    def _update_company_data(self, company_data: CompanyInfo, customer_id: str) -> None:
        existing_company_data = self._get_company_data_by_customer(customer_id)

        updated_address = self._create_address(company_data.address)
        updated_address.id = existing_company_data.address_id
        self.db.merge(updated_address)

        updated_company_data = self._create_company_data(
            company_data=company_data, address_id=existing_company_data.address_id, customer_id=customer_id
        )
        updated_company_data.id = existing_company_data.id
        self.db.merge(updated_company_data)

    def _update_contact_persons(self, contact_persons: ContactPersonsReadOnly, customer_id: str) -> None:
        new_contact_persons = self._create_contact_persons_and_methods(
            contact_persons=contact_persons, customer_id=customer_id
        )
        existing_contact_persons = self._get_contact_persons_by_customer(customer_id=customer_id)

        new_persons_set = {person.personal_info.id for person in new_contact_persons}
        existing_persons_set = {person.id for person in existing_contact_persons}

        to_add = new_persons_set - existing_persons_set
        to_update = new_persons_set & existing_persons_set
        to_delete = existing_persons_set - new_persons_set

        for person in existing_contact_persons:
            if person.id in to_delete:
                self.db.delete(person)
            if person.id in to_update:
                for contact_method in person.contact_methods:
                    self.db.delete(contact_method)

        for person in new_contact_persons:
            if person.personal_info.id in to_add:
                self.db.add(person.personal_info)
                self.db.add_all(person.contact_methods)
            if person.personal_info.id in to_update:
                self.db.merge(person.personal_info)
                self.db.add_all(person.contact_methods)

    def _create_contact_persons_and_methods(
        self, contact_persons: ContactPersonsReadOnly, customer_id: str
    ) -> Iterable[ContactPersonDbData]:
        persons_data = []
        for person in contact_persons:
            language = person.preferred_language
            language_id = self._get_language_id_by_code_and_name(code=language.code, name=language.name)
            person_in_db = ContactPersonModel.from_domain(
                entity=person, language_id=language_id, customer_id=customer_id
            )
            contact_methods_in_db = self._create_contact_methods(
                contact_methods=person.contact_methods, person_id=person.id
            )
            persons_data.append(ContactPersonDbData(personal_info=person_in_db, contact_methods=contact_methods_in_db))
        return persons_data

    def _create_contact_methods(self, contact_methods: ContactMethods, person_id: str) -> Iterable[ContactMethodModel]:
        methods = tuple(
            ContactMethodModel.from_domain(entity=method, contact_person_id=person_id) for method in contact_methods
        )
        return methods

    def _create_address(self, address: Address) -> AddressModel:
        country_id = self._get_country_id_by_name_and_code(name=address.country.name, code=address.country.code)
        address_in_db = AddressModel.from_domain(entity=address, country_id=country_id)
        return address_in_db

    def _create_company_data(self, company_data: CompanyInfo, address_id: str, customer_id: str) -> CompanyDataModel:
        company_data_in_db = CompanyDataModel.from_domain(
            entity=company_data, address_id=address_id, customer_id=customer_id
        )
        return company_data_in_db

    def _get_language_id_by_code_and_name(self, code: str, name: str) -> str:
        query = select(LanguageModel.id).where(LanguageModel.name == name, LanguageModel.code == code)
        language_id = self.db.scalar(query)
        if not language_id:
            raise InvalidData("Invalid language")
        return language_id

    def _get_country_id_by_name_and_code(self, name: str, code: str) -> str:
        query = select(CountryModel.id).where(CountryModel.name == name, CountryModel.code == code)
        country_id = self.db.scalar(query)
        if not country_id:
            raise InvalidData("Invalid address country")
        return country_id

    def _get_contact_persons_by_customer(self, customer_id: str) -> Iterable[ContactPersonModel]:
        query = select(ContactPersonModel).where(ContactPersonModel.customer_id == customer_id)
        persons = self.db.scalars(query).all()
        return persons

    def _get_company_data_by_customer(self, customer_id: str) -> CompanyDataModel:
        query = select(CompanyDataModel).where(CompanyDataModel.customer_id == customer_id)
        data = self.db.scalar(query)
        if data is None:
            raise ServerError("Company data of the given customer cannot be found")
        return data

    def _get_address(self, address_id: str) -> AddressModel:
        query = select(AddressModel).where(AddressModel.id == address_id)
        address = self.db.scalar(query)
        if address is None:
            raise ServerError("Address of the given customer cannot be found")
        return address

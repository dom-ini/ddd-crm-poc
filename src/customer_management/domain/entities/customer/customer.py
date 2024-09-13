from typing import Self

from attrs import define, field
from building_blocks.domain.entity import AggregateRoot
from building_blocks.domain.validators import validate_no_duplicates
from customer_management.domain.entities.customer.validators import (
    at_least_one_contact_person,
)
from customer_management.domain.exceptions import ContactPersonDoesNotExist
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.entities.contact_person import (
    ContactPerson,
    ContactPersonReadOnly,
    ContactMethods,
)
from customer_management.domain.value_objects.customer_status import (
    CustomerStatus,
    InitialStatus,
)
from customer_management.domain.value_objects.language import Language


ContactPersons = tuple[ContactPerson, ...]
ContactPersonsReadOnly = tuple[ContactPersonReadOnly, ...]


def get_unique_contact_person_fields(contact_person: ContactPerson) -> tuple:
    return (
        contact_person.first_name,
        contact_person.last_name,
        contact_person.contact_methods,
    )


@define(eq=False, kw_only=True)
class Customer(AggregateRoot):
    company_info: CompanyInfo
    _relation_manager_id: str = field(alias="relation_manager_id")
    _status: CustomerStatus = field(init=False)
    _contact_persons: ContactPersons = field(init=False, factory=tuple)

    @classmethod
    def reconstitute(
        cls,
        *,
        id: str,
        relation_manager_id: str,
        company_info: CompanyInfo,
        status: CustomerStatus,
        contact_persons: ContactPersons,
    ) -> Self:
        customer = cls(
            id=id, relation_manager_id=relation_manager_id, company_info=company_info
        )
        customer._status = status
        customer._contact_persons = contact_persons
        return customer

    @_status.default
    def _get_default_status(self) -> CustomerStatus:
        return InitialStatus(self)

    @property
    def contact_persons(self) -> ContactPersonsReadOnly:
        read_only_contact_persons = tuple(
            person.to_read_only() for person in self._contact_persons
        )
        return read_only_contact_persons

    @property
    def status(self) -> CustomerStatus:
        return self._status

    @property
    def relation_manager_id(self) -> str:
        return self._relation_manager_id

    def change_relation_manager(self, new_relation_manager_id: str) -> Self:
        self._relation_manager_id = new_relation_manager_id
        return self

    def convert(self) -> Self:
        self._status.convert()
        return self

    def archive(self) -> Self:
        self._status.archive()
        return self

    def add_contact_person(
        self,
        contact_person_id: str,
        first_name: str,
        last_name: str,
        job_title: str,
        preferred_language: Language,
        contact_methods: ContactMethods,
    ) -> Self:
        contact_person = self._create_contact_person(
            contact_person_id=contact_person_id,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            preferred_language=preferred_language,
            contact_methods=contact_methods,
        )
        new_contact_persons = self._contact_persons + (contact_person,)
        validate_no_duplicates(
            new_contact_persons, callback=get_unique_contact_person_fields
        )
        self._contact_persons = new_contact_persons
        return self

    def remove_contact_person(self, id_to_remove: str) -> Self:
        new_contact_persons = tuple(
            person for person in self._contact_persons if id_to_remove != person.id
        )
        if len(new_contact_persons) == len(self._contact_persons):
            raise ContactPersonDoesNotExist
        self._contact_persons = new_contact_persons
        return self

    def _create_contact_person(
        self,
        contact_person_id: str,
        first_name: str,
        last_name: str,
        job_title: str,
        preferred_language: Language,
        contact_methods: ContactMethods,
    ) -> ContactPerson:
        contact_person = ContactPerson(
            id=contact_person_id,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            preferred_language=preferred_language,
            contact_methods=contact_methods,
        )
        return contact_person

    def _add_contact_persons(self, contact_persons: ContactPersons) -> None:
        validate_no_duplicates(contact_persons, callback=lambda x: x.first_name)
        self._contact_persons = self._contact_persons + contact_persons

    def _validate_contact_persons_by_status(
        self, contact_persons: ContactPersons
    ) -> None:
        at_least_one_contact_person(contact_persons)

    def _change_status(self, status: CustomerStatus) -> Self:
        self._status = status
        return self

    def __str__(self) -> str:
        return f"Customer: {self.company_info}"

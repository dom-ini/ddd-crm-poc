from collections.abc import Iterable
from typing import Self

from attrs import define, field

from building_blocks.domain.entity import AggregateRoot
from building_blocks.domain.validators import validate_no_duplicates
from customer_management.domain.entities.contact_person import ContactPerson, ContactPersonReadOnly
from customer_management.domain.entities.contact_person.validators import ContactMethod
from customer_management.domain.entities.customer.validators import at_least_one_contact_person
from customer_management.domain.exceptions import (
    ContactPersonAlreadyExists,
    ContactPersonDoesNotExist,
    OnlyRelationManagerCanChangeStatus,
    OnlyRelationManagerCanModifyCustomerData,
)
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.customer_status import CustomerStatus, InitialStatus
from customer_management.domain.value_objects.language import Language

ContactPersons = Iterable[ContactPerson]
ContactPersonsReadOnly = Iterable[ContactPersonReadOnly]


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
        customer = cls(id=id, relation_manager_id=relation_manager_id, company_info=company_info)
        customer._status = status
        customer._contact_persons = contact_persons
        return customer

    def update(
        self,
        editor_id: str,
        relation_manager_id: str | None = None,
        company_info: CompanyInfo | None = None,
    ) -> None:
        self._check_update_permissions(editor_id)
        if relation_manager_id is not None:
            self._relation_manager_id = relation_manager_id
        if company_info is not None:
            self.company_info = company_info

    @_status.default
    def _get_default_status(self) -> CustomerStatus:
        return InitialStatus(self)

    @property
    def contact_persons(self) -> ContactPersonsReadOnly:
        read_only_contact_persons = tuple(person.to_read_only() for person in self._contact_persons)
        return read_only_contact_persons

    @property
    def status(self) -> CustomerStatus:
        return self._status

    @property
    def relation_manager_id(self) -> str:
        return self._relation_manager_id

    def convert(self, requestor_id: str) -> None:
        self._check_status_change_permissions(requestor_id)
        self._status.convert()

    def archive(self, requestor_id: str) -> None:
        self._check_status_change_permissions(requestor_id)
        self._status.archive()

    def get_contact_person(self, contact_person_id: str) -> ContactPerson:
        _, contact_person = self._get_contact_person_by_id(contact_person_id)
        return contact_person

    def add_contact_person(
        self,
        editor_id: str,
        contact_person_id: str,
        first_name: str,
        last_name: str,
        job_title: str,
        preferred_language: Language,
        contact_methods: Iterable[ContactMethod],
    ) -> None:
        self._check_update_permissions(editor_id)
        self._check_if_contact_person_id_is_used(contact_person_id)
        contact_person = self._create_contact_person(
            contact_person_id=contact_person_id,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            preferred_language=preferred_language,
            contact_methods=contact_methods,
        )
        new_contact_persons = self._contact_persons + (contact_person,)
        self._set_contact_persons_if_valid(new_contact_persons)

    def update_contact_person(
        self,
        editor_id: str,
        contact_person_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        job_title: str | None = None,
        preferred_language: Language | None = None,
        contact_methods: Iterable[ContactMethod] | None = None,
    ) -> None:
        self._check_update_permissions(editor_id)
        index, contact_person = self._get_contact_person_by_id(contact_person_id)
        new_contact_person = self._create_contact_person_with_default_values(
            contact_person=contact_person,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            preferred_language=preferred_language,
            contact_methods=contact_methods,
        )
        new_contact_persons = self._contact_persons[:index] + (new_contact_person,) + self._contact_persons[index + 1 :]
        self._set_contact_persons_if_valid(new_contact_persons)

    def remove_contact_person(self, editor_id: str, id_to_remove: str) -> None:
        self._check_update_permissions(editor_id)
        new_contact_persons = tuple(person for person in self._contact_persons if id_to_remove != person.id)
        if len(new_contact_persons) == len(self._contact_persons):
            raise ContactPersonDoesNotExist
        self._contact_persons = new_contact_persons

    def _check_update_permissions(self, editor_id: str) -> None:
        if editor_id != self.relation_manager_id:
            raise OnlyRelationManagerCanModifyCustomerData

    def _check_if_contact_person_id_is_used(self, id_to_check: str) -> None:
        try:
            self.get_contact_person(id_to_check)
            raise ContactPersonAlreadyExists(id_to_check)
        except ContactPersonDoesNotExist:
            pass

    def _create_contact_person_with_default_values(
        self,
        contact_person: ContactPerson,
        first_name: str | None = None,
        last_name: str | None = None,
        job_title: str | None = None,
        preferred_language: Language | None = None,
        contact_methods: Iterable[ContactMethod] | None = None,
    ) -> ContactPerson:
        id_ = contact_person.id
        new_first_name = first_name or contact_person.first_name
        new_last_name = last_name or contact_person.last_name
        new_job_title = job_title or contact_person.job_title
        new_preferred_language = preferred_language or contact_person.preferred_language
        new_contact_methods = contact_methods or contact_person.contact_methods
        new_contact_person = self._create_contact_person(
            contact_person_id=id_,
            first_name=new_first_name,
            last_name=new_last_name,
            job_title=new_job_title,
            preferred_language=new_preferred_language,
            contact_methods=new_contact_methods,
        )
        return new_contact_person

    def _set_contact_persons_if_valid(self, contact_persons: ContactPersons) -> None:
        validate_no_duplicates(contact_persons, callback=get_unique_contact_person_fields)
        self._contact_persons = contact_persons

    def _get_contact_person_by_id(self, contact_person_id: str) -> tuple[int, ContactPerson]:
        persons_ids = ((i, person) for i, person in enumerate(self._contact_persons) if person.id == contact_person_id)
        id_, contact_person = next(persons_ids, (None, None))
        if id_ is None:
            raise ContactPersonDoesNotExist
        return id_, contact_person

    def _create_contact_person(
        self,
        contact_person_id: str,
        first_name: str,
        last_name: str,
        job_title: str,
        preferred_language: Language,
        contact_methods: Iterable[ContactMethod],
    ) -> ContactPerson:
        contact_person = ContactPerson(
            id=contact_person_id,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            preferred_language=preferred_language,
            contact_methods=tuple(contact_methods),
        )
        return contact_person

    def _validate_contact_persons_called_by_status(self, contact_persons: ContactPersons) -> None:
        at_least_one_contact_person(contact_persons)

    def _check_status_change_permissions(self, requestor_id: str) -> None:
        if requestor_id != self.relation_manager_id:
            raise OnlyRelationManagerCanChangeStatus

    def _change_status(self, status: CustomerStatus) -> None:
        self._status = status

    def __str__(self) -> str:
        return f"Customer: {self.company_info}"

from collections.abc import Iterable, Sequence

from attrs import Attribute, define, field

from building_blocks.domain.entity import Entity, ReadOnlyEntity
from building_blocks.domain.validators import validate_no_duplicates
from customer_management.domain.entities.contact_person.validators import at_least_one_preferred_contact_method
from customer_management.domain.value_objects.contact_method import ContactMethod
from customer_management.domain.value_objects.language import Language

ContactMethods = Sequence[ContactMethod]


def get_unique_contact_method_fields(contact_method: ContactMethod) -> Iterable:
    return (contact_method.type, contact_method.value)


@define(eq=False, kw_only=True)
class ContactPerson(Entity):
    id: str
    first_name: str
    last_name: str
    job_title: str
    preferred_language: Language
    _contact_methods: ContactMethods = field(alias="contact_methods")

    @property
    def contact_methods(self) -> ContactMethods:
        return self._contact_methods

    @_contact_methods.validator
    def _validate_contact_methods(self, _attribute: Attribute, value: ContactMethods) -> None:
        validate_no_duplicates(value, get_unique_contact_method_fields)
        at_least_one_preferred_contact_method(value)

    def to_read_only(self) -> "ContactPersonReadOnly":
        return ContactPersonReadOnly(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            job_title=self.job_title,
            preferred_language=self.preferred_language,
            contact_methods=self.contact_methods,
        )

    def __str__(self) -> str:
        return f"Contact person: {self.first_name} {self.last_name} ({self.job_title})"


@define(eq=False, kw_only=True, frozen=True)
class ContactPersonReadOnly(ReadOnlyEntity):
    id: str
    first_name: str
    last_name: str
    job_title: str
    preferred_language: Language
    contact_methods: ContactMethods

    def __str__(self) -> str:
        return f"Contact person: {self.first_name} {self.last_name} ({self.job_title})"

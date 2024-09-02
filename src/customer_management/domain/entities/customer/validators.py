from typing import Iterable
from customer_management.domain.exceptions import NotEnoughContactPersons


ContactPersons = Iterable


def at_least_one_contact_person(
    contact_persons: ContactPersons,
) -> None:
    if len(contact_persons) < 1:
        raise NotEnoughContactPersons

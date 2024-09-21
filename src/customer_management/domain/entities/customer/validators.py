from typing import Iterable

from customer_management.domain.exceptions import NotEnoughContactPersons


def at_least_one_contact_person(
    contact_persons: Iterable,
) -> None:
    if len(contact_persons) < 1:
        raise NotEnoughContactPersons

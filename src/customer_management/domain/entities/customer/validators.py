from collections.abc import Sequence

from customer_management.domain.exceptions import NotEnoughContactPersons


def at_least_one_contact_person(
    contact_persons: Sequence,
) -> None:
    if len(contact_persons) < 1:
        raise NotEnoughContactPersons

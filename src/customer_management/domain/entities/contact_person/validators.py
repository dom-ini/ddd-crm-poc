from collections.abc import Iterable
from typing import Protocol
from customer_management.domain.exceptions import NotEnoughPreferredContactMethods


class ContactMethod(Protocol):
    is_preferred: bool


ContactMethods = Iterable[ContactMethod]


def at_least_one_preferred_contact_method(methods: ContactMethods) -> None:
    if not any(method.is_preferred for method in methods):
        raise NotEnoughPreferredContactMethods

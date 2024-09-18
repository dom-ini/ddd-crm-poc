from building_blocks.domain.exceptions import DomainException


class NotEnoughContactPersons(DomainException):
    message = "Customer should have at least one contact person"


class NotEnoughPreferredContactMethods(DomainException):
    message = "Contact person should have at least one preferred contact method"


class CannotConvertArchivedCustomer(DomainException):
    message = "Archived customer cannot be converted again"


class CustomerAlreadyConverted(DomainException):
    message = "Customer is already converted"


class CustomerAlreadyArchived(DomainException):
    message = "Customer is already archived"


class ContactPersonDoesNotExist(DomainException):
    message = "Given contact person is not a contact person of this customer"


class OnlyRelationManagerCanChangeStatus(DomainException):
    message = "Only relation manager can change status"

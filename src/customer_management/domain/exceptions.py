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


class ContactPersonAlreadyExists(DomainException):
    def __init__(self, id_: str) -> None:
        self.message = f"Contact person with id={id_} already exists"
        super().__init__()


class OnlyRelationManagerCanChangeStatus(DomainException):
    message = "Only relation manager can change status"


class OnlyRelationManagerCanModifyCustomerData(DomainException):
    message = "Only relation manager can modify customer data"


class CustomerStillHasNotClosedOpportunities(DomainException):
    message = "Customer still has not closed opportunities"


class InvalidCustomerStatus(DomainException):
    message = "Given status is not a valid customer status"

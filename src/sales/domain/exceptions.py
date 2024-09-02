from building_blocks.domain.exceptions import DomainException


class OnlyOwnerCanEditNotes(DomainException):
    message = "Only owner can edit notes"


class UnauthorizedLeadOwnerChange(DomainException):
    message = "Only lead owner can assign a lead"


class EmailOrPhoneNumberShouldBeSet(DomainException):
    message = "Email address or phone number must be set"

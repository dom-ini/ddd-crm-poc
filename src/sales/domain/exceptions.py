from building_blocks.domain.exceptions import DomainException


class OnlyOwnerCanEditNotes(DomainException):
    message = "Only owner can edit notes"


class OnlyOwnerCanModifyOffer(DomainException):
    message = "Only owner can modify offer"


class OnlyOwnerCanModifyOpportunityData(DomainException):
    message = "Only owner can modify opportunity data"


class OnlyOwnerCanModifyLeadData(DomainException):
    message = "Only owner can modify lead data"


class UnauthorizedLeadOwnerChange(DomainException):
    message = "Only lead owner can assign a lead"


class EmailOrPhoneNumberShouldBeSet(DomainException):
    message = "Email address or phone number must be set"


class AmountMustBeGreaterThanZero(DomainException):
    message = "Amount must be greaten than 0"


class SalesRepresentativeCanOnlyModifyItsOwnData(DomainException):
    message = "Sales representative can only modify its own data"

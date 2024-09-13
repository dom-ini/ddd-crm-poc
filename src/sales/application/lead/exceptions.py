from building_blocks.application.exceptions import ApplicationException


class LeadDoesNotExist(ApplicationException):
    message = "The specified lead does not exist"


class InvalidLeadData(ApplicationException):
    pass

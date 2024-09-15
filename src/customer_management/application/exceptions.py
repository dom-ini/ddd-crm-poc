from building_blocks.application.exceptions import ApplicationException


class CustomerDoesNotExist(ApplicationException):
    message = "The specified customer does not exist"

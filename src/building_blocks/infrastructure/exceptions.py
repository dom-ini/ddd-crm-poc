class InfrastructureException(Exception):
    message: str = ""

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class TransactionAlreadyActive(InfrastructureException):
    message = "Transaction is already started"


class NoActiveTransaction(InfrastructureException):
    pass


class ObjectAlreadyExists(InfrastructureException):
    pass


class ServerError(InfrastructureException):
    message = "An error occured while processing the request. Try again or contact the site administrator"


class InvalidFilterField(InfrastructureException):
    def __init__(self, field: str) -> None:
        message = f'Invalid filter chain: "{field}"'
        super().__init__(message)

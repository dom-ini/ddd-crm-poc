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


class ObjectDoesNotExist(InfrastructureException):
    pass

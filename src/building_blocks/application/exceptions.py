class ApplicationException(Exception):
    message: str = ""

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class InvalidFilterType(ApplicationException):
    message = "No filter function defined for given filter type"


class ForbiddenAction(ApplicationException):
    pass


class ConfictingAction(ApplicationException):
    pass


class ObjectDoesNotExist(ApplicationException):
    def __init__(self, id_: str) -> None:
        message = f"Object with id={id_} does not exist"
        super().__init__(message)


class InvalidData(ApplicationException):
    pass

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

class ApplicationException(Exception):
    message: str

    def __str__(self) -> str:
        return self.message

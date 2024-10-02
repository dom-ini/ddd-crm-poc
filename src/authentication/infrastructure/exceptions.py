from building_blocks.infrastructure.exceptions import InfrastructureException


class InvalidToken(InfrastructureException):
    message = "Invalid token"

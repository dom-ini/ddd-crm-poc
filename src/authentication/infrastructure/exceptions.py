from building_blocks.infrastructure.exceptions import InfrastructureException


class InvalidToken(InfrastructureException):
    message = "Invalid token"


class InvalidUserCreationData(InfrastructureException):
    message = "Invalid user creation data"


class AccountDisabled(InfrastructureException):
    message = "This user account is disabled"


class AuthenticationServiceFailed(InfrastructureException):
    message = "An error occured in the authentication service"

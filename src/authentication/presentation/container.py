from typing import Protocol

from authentication.infrastructure.service.base import AuthenticationService


class AuthApplicationContainer(Protocol):
    auth_service: AuthenticationService

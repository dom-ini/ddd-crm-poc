from typing import Protocol

from fastapi import Request

from authentication.infrastructure.service.base import AuthenticationService


class AuthApplicationContainer(Protocol):
    auth_service: AuthenticationService


def get_container(request: Request) -> AuthApplicationContainer:
    return request.app.state.container

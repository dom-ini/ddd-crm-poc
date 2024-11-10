from fastapi import Request

from authentication.presentation.container import AuthApplicationContainer


def get_container(request: Request) -> AuthApplicationContainer:
    return request.app.state.container

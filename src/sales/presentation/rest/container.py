from fastapi import Request

from sales.presentation.container import SalesApplicationContainer


def get_container(request: Request) -> SalesApplicationContainer:
    return request.app.state.container

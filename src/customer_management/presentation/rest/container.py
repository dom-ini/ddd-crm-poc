from fastapi import Request

from customer_management.presentation.container import CustomerManagementApplicationContainer


def get_container(request: Request) -> CustomerManagementApplicationContainer:
    return request.app.state.container

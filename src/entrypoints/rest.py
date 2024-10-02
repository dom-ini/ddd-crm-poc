from fastapi import FastAPI

from authentication.presentation.rest.api import router as auth_router
from containers.container import ApplicationContainer
from containers.file import FileApplicationContainer
from customer_management.presentation.rest.api import router as customer_management_router
from sales.presentation.rest.api import router as sales_router


def bind_container(instance: FastAPI, container: ApplicationContainer) -> None:
    instance.state.container = container


app = FastAPI(title="CRM DDD PoC")

app.include_router(auth_router)
app.include_router(customer_management_router)
app.include_router(sales_router)

bind_container(app, FileApplicationContainer())

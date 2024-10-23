from dotenv import load_dotenv
from fastapi import FastAPI

from authentication.presentation.rest.api import router as auth_router
from containers.config import ContainerManager
from containers.container import ApplicationContainer
from customer_management.presentation.rest.api import router as customer_management_router
from sales.presentation.rest.api import router as sales_router


def bind_container(instance: FastAPI, container: ApplicationContainer) -> None:
    instance.state.container = container


load_dotenv()

app = FastAPI(title="CRM DDD PoC")

app.include_router(auth_router)
app.include_router(customer_management_router)
app.include_router(sales_router)

app_container = ContainerManager.build()
bind_container(app, app_container)

from fastapi import FastAPI

from customer_management.presentation.rest.api import (
    router as customer_management_router,
)
from sales.presentation.rest.api import router as sales_router


app = FastAPI()
app.include_router(customer_management_router)
app.include_router(sales_router)

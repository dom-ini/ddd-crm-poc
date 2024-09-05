from fastapi import FastAPI

from sales.presentation.rest.api import router as sales_router


app = FastAPI()
app.include_router(sales_router)

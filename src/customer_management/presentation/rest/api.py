from fastapi import APIRouter

from customer_management.presentation.rest.customer.api import router as customer_router
from customer_management.presentation.rest.value_objects.api import router as vo_router

router = APIRouter()
router.include_router(customer_router)
router.include_router(vo_router)

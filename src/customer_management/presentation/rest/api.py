from fastapi import APIRouter, status

from building_blocks.presentation.responses import BasicErrorResponse
from customer_management.presentation.rest.customer.api import router as customer_router
from customer_management.presentation.rest.value_objects.api import router as vo_router

router = APIRouter(responses={status.HTTP_401_UNAUTHORIZED: {"model": BasicErrorResponse}})
router.include_router(customer_router)
router.include_router(vo_router)

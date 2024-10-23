from fastapi import APIRouter

from sales.presentation.rest.lead.api import router as lead_router
from sales.presentation.rest.opportunity.api import router as opportunity_router
from sales.presentation.rest.sales_representative.api import router as sr_router
from sales.presentation.rest.value_objects.api import router as vo_router

router = APIRouter()
router.include_router(lead_router)
router.include_router(opportunity_router)
router.include_router(sr_router)
router.include_router(vo_router)

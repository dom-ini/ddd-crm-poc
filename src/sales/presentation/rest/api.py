from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, status

from sales.application.lead.exceptions import LeadDoesNotExist
from sales.application.lead.query import LeadQueryUseCase
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.notes.query_model import NoteReadModel
from sales.infrastructure.json.lead.query_service import LeadJsonQueryService


router = APIRouter(prefix="/leads", tags=["leads"])


def get_lead_query_use_case() -> LeadQueryUseCase:
    lead_query_service = LeadJsonQueryService()
    return LeadQueryUseCase(lead_query_service)


@router.get(
    "/",
    response_model=list[LeadReadModel],
)
async def get_leads(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    customer_id: str | None = None,
    salesman_id: str | None = None,
):
    if customer_id or salesman_id:
        leads = lead_query_usecase.get_by_customer_and_owner(
            owner_id=salesman_id, customer_id=customer_id
        )
    else:
        leads = lead_query_usecase.get_all()
    return leads


@router.get(
    "/{lead_id}",
    response_model=LeadReadModel,
)
async def get_single_lead(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
):
    try:
        lead = lead_query_usecase.get(lead_id)
    except LeadDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return lead


@router.get(
    "/{lead_id}/assignments",
    response_model=list[AssignmentReadModel],
)
async def get_lead_assignments(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
):
    try:
        assignments = lead_query_usecase.get_assignment_history(lead_id)
    except LeadDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return assignments


@router.get(
    "/{lead_id}/notes",
    response_model=list[NoteReadModel],
)
async def get_lead_notes(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
):
    try:
        notes = lead_query_usecase.get_notes(lead_id)
    except LeadDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return notes


app = FastAPI()
app.include_router(router)

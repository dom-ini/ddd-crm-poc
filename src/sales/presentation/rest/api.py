from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Path, status

from building_blocks.infrastructure.exceptions import ObjectDoesNotExist
from sales.application.lead.command import LeadCommandUseCase
from sales.application.lead.command_model import (
    AssignmentUpdateModel,
    LeadCreateModel,
    LeadUpdateModel,
)
from sales.application.lead.exceptions import InvalidLeadData, LeadDoesNotExist
from sales.application.lead.query import LeadQueryUseCase
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.notes.query_model import NoteReadModel
from sales.infrastructure.file.lead.command import LeadFileUnitOfWork
from sales.application.notes.command_model import NoteCreateModel
from sales.infrastructure.file import config as file_config
from sales.infrastructure.file.lead.query_service import LeadFileQueryService
from sales.domain.exceptions import OnlyOwnerCanEditNotes


router = APIRouter(prefix="/leads", tags=["leads"])


def get_lead_query_use_case() -> LeadQueryUseCase:
    lead_query_service = LeadFileQueryService()
    return LeadQueryUseCase(lead_query_service)


def get_lead_command_use_case() -> LeadCommandUseCase:
    lead_uow = LeadFileUnitOfWork(file_config.LEADS_FILE_PATH)
    return LeadCommandUseCase(lead_uow)


@router.get(
    "/",
    response_model=list[LeadReadModel],
)
def get_leads(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    customer_id: str | None = None,
    salesman_id: str | None = None,
    contact_company_name: str | None = None,
    contact_phone: str | None = None,
    contact_email: str | None = None,
) -> None:
    leads = lead_query_usecase.get_filtered(
        owner_id=salesman_id,
        customer_id=customer_id,
        contact_company_name=contact_company_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
    )
    return leads


@router.post("/", response_model=LeadReadModel)
def create_lead(
    lead_command_usecase: Annotated[
        LeadCommandUseCase, Depends(get_lead_command_use_case)
    ],
    data: LeadCreateModel,
) -> None:
    try:
        book = lead_command_usecase.create(lead_data=data, creator_id=str(uuid4()))
    except InvalidLeadData as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
        )
    return book


@router.get(
    "/{lead_id}",
    response_model=LeadReadModel,
)
def get_single_lead(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
) -> None:
    try:
        lead = lead_query_usecase.get(lead_id)
    except LeadDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return lead


@router.put("/{lead_id}", response_model=LeadReadModel)
def update_lead(
    lead_command_usecase: Annotated[
        LeadCommandUseCase, Depends(get_lead_command_use_case)
    ],
    data: LeadUpdateModel,
    lead_id: Annotated[str, Path],
) -> None:
    try:
        book = lead_command_usecase.update(lead_id=lead_id, lead_data=data)
    except InvalidLeadData as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
        )
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return book


@router.get(
    "/{lead_id}/assignments",
    response_model=list[AssignmentReadModel],
)
def get_lead_assignments(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
) -> None:
    try:
        assignments = lead_query_usecase.get_assignment_history(lead_id)
    except LeadDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return assignments


@router.post("/{lead_id}/assignments", response_model=AssignmentReadModel)
def assign_salesman(
    lead_command_usecase: Annotated[
        LeadCommandUseCase, Depends(get_lead_command_use_case)
    ],
    data: AssignmentUpdateModel,
    lead_id: Annotated[str, Path],
    creator_id: Annotated[str, Path],  # TODO: wywalić!!!
) -> None:
    try:
        note = lead_command_usecase.update_assignment(
            lead_id=lead_id, requestor_id=creator_id, assignment_data=data
        )
    except OnlyOwnerCanEditNotes as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    return note


@router.get(
    "/{lead_id}/notes",
    response_model=list[NoteReadModel],
)
def get_lead_notes(
    lead_query_usecase: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
) -> None:
    try:
        notes = lead_query_usecase.get_notes(lead_id)
    except LeadDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return notes


@router.post("/{lead_id}/notes", response_model=NoteReadModel)
def create_note(
    lead_command_usecase: Annotated[
        LeadCommandUseCase, Depends(get_lead_command_use_case)
    ],
    data: NoteCreateModel,
    lead_id: Annotated[str, Path],
    creator_id: Annotated[str, Path],  # TODO: wywalić!!!
) -> None:
    try:
        note = lead_command_usecase.update_note(
            lead_id=lead_id, editor_id=creator_id, note_data=data
        )
    except OnlyOwnerCanEditNotes as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    return note

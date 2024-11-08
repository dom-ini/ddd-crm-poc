from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from authentication.infrastructure.service.base import UserReadModel
from authentication.presentation.rest.deps import get_current_user
from building_blocks.application.exceptions import ConflictingAction, ForbiddenAction, InvalidData, ObjectDoesNotExist
from building_blocks.presentation.responses import BasicErrorResponse, UnprocessableEntityResponse
from sales.application.lead.command import LeadCommandUseCase
from sales.application.lead.command_model import AssignmentUpdateModel, LeadCreateModel, LeadUpdateModel
from sales.application.lead.query import LeadQueryUseCase
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.notes.command_model import NoteCreateModel
from sales.application.notes.query_model import NoteReadModel
from sales.presentation.container import get_container

router = APIRouter(prefix="/leads", tags=["leads"], dependencies=[Depends(get_current_user)])


def get_lead_query_use_case(request: Request) -> LeadQueryUseCase:
    container = get_container(request)
    return container.lead_query_use_case


def get_lead_command_use_case(request: Request) -> LeadCommandUseCase:
    container = get_container(request)
    return container.lead_command_use_case


@router.get(
    "/",
    response_model=list[LeadReadModel],
)
def get_leads(
    lead_query_use_case: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    customer_id: str | None = None,
    salesman_id: str | None = None,
    contact_phone: str | None = None,
    contact_email: str | None = None,
) -> None:
    leads = lead_query_use_case.get_filtered(
        owner_id=salesman_id,
        customer_id=customer_id,
        contact_phone=contact_phone,
        contact_email=contact_email,
    )
    return leads


@router.post(
    "/",
    response_model=LeadReadModel,
    responses={status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse}},
)
def create_lead(
    lead_command_use_case: Annotated[LeadCommandUseCase, Depends(get_lead_command_use_case)],
    data: LeadCreateModel,
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        lead = lead_command_use_case.create(lead_data=data, creator_id=current_user.salesman_id)
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return lead


@router.get(
    "/{lead_id}",
    response_model=LeadReadModel,
    responses={status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse}},
)
def get_single_lead(
    lead_query_use_case: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
) -> None:
    try:
        lead = lead_query_use_case.get(lead_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return lead


@router.put(
    "/{lead_id}",
    response_model=LeadReadModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def update_lead(
    lead_command_use_case: Annotated[LeadCommandUseCase, Depends(get_lead_command_use_case)],
    data: LeadUpdateModel,
    lead_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        lead = lead_command_use_case.update(lead_id=lead_id, editor_id=current_user.salesman_id, lead_data=data)
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return lead


@router.get(
    "/{lead_id}/assignments",
    response_model=list[AssignmentReadModel],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def get_lead_assignments(
    lead_query_use_case: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
) -> None:
    try:
        assignments = lead_query_use_case.get_assignment_history(lead_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return assignments


@router.post(
    "/{lead_id}/assignments",
    response_model=AssignmentReadModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status.HTTP_409_CONFLICT: {"model": BasicErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def assign_salesman(
    lead_command_use_case: Annotated[LeadCommandUseCase, Depends(get_lead_command_use_case)],
    data: AssignmentUpdateModel,
    lead_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        note = lead_command_use_case.update_assignment(
            lead_id=lead_id, requestor_id=current_user.salesman_id, assignment_data=data
        )
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ConflictingAction as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return note


@router.get(
    "/{lead_id}/notes",
    response_model=list[NoteReadModel],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def get_lead_notes(
    lead_query_use_case: Annotated[LeadQueryUseCase, Depends(get_lead_query_use_case)],
    lead_id: Annotated[str, Path],
) -> None:
    try:
        notes = lead_query_use_case.get_notes(lead_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return notes


@router.post(
    "/{lead_id}/notes",
    response_model=NoteReadModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def create_note(
    lead_command_use_case: Annotated[LeadCommandUseCase, Depends(get_lead_command_use_case)],
    data: NoteCreateModel,
    lead_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        note = lead_command_use_case.update_note(lead_id=lead_id, editor_id=current_user.salesman_id, note_data=data)
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return note

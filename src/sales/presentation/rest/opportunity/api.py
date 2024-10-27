from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from authentication.infrastructure.service.base import UserReadModel
from authentication.presentation.rest.deps import get_current_user
from building_blocks.application.exceptions import ForbiddenAction, InvalidData, ObjectDoesNotExist
from building_blocks.presentation.responses import BasicErrorResponse, UnprocessableEntityResponse
from sales.application.notes.command_model import NoteCreateModel
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.opportunity.command_model import (
    OfferItemCreateUpdateModel,
    OpportunityCreateModel,
    OpportunityUpdateModel,
)
from sales.application.opportunity.query import OpportunityQueryUseCase
from sales.application.opportunity.query_model import OfferItemReadModel, OpportunityReadModel
from sales.domain.value_objects.opportunity_stage import OpportunityStageName
from sales.domain.value_objects.priority import PriorityLevel
from sales.presentation.container import get_container

router = APIRouter(prefix="/opportunities", tags=["opportunities"], dependencies=[Depends(get_current_user)])


def get_op_query_use_case(request: Request) -> OpportunityQueryUseCase:
    container = get_container(request)
    return container.opportunity_query_use_case


def get_op_command_use_case(request: Request) -> OpportunityCommandUseCase:
    container = get_container(request)
    return container.opportunity_command_use_case


@router.get("/", response_model=list[OpportunityReadModel])
def get_opportunities(
    op_query_use_case: Annotated[OpportunityQueryUseCase, Depends(get_op_query_use_case)],
    customer_id: str | None = None,
    owner_id: str | None = None,
    stage: OpportunityStageName | None = None,
    priority: PriorityLevel | None = None,
) -> None:
    opportunities = op_query_use_case.get_filtered(
        customer_id=customer_id, owner_id=owner_id, stage=stage, priority=priority
    )
    return opportunities


@router.post(
    "/",
    response_model=OpportunityReadModel,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def create_opportunity(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: OpportunityCreateModel,
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        opportunity = op_command_use_case.create(data=data, creator_id=current_user.salesman_id)
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return opportunity


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityReadModel,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def get_single_opportunity(
    op_query_use_case: Annotated[OpportunityQueryUseCase, Depends(get_op_query_use_case)],
    opportunity_id: Annotated[str, Path],
) -> None:
    try:
        opportunity = op_query_use_case.get(opportunity_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return opportunity


@router.put(
    "/{opportunity_id}",
    response_model=OpportunityReadModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def update_opportunity(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: OpportunityUpdateModel,
    opportunity_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        opportunity = op_command_use_case.update(
            opportunity_id=opportunity_id, editor_id=current_user.salesman_id, data=data
        )
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return opportunity


@router.get(
    "/{opportunity_id}/offer-items",
    response_model=list[OfferItemReadModel],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def get_opportunity_offer(
    op_query_use_case: Annotated[OpportunityQueryUseCase, Depends(get_op_query_use_case)],
    opportunity_id: Annotated[str, Path],
) -> None:
    try:
        offer = op_query_use_case.get_offer(opportunity_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return offer


@router.put(
    "/{opportunity_id}/offer-items",
    response_model=list[OfferItemReadModel],
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def update_opportunity_offer(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: list[OfferItemCreateUpdateModel],
    opportunity_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        offer_items = op_command_use_case.update_offer(
            opportunity_id=opportunity_id, editor_id=current_user.salesman_id, data=data
        )
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    return offer_items


@router.get(
    "/{opportunity_id}/notes",
    response_model=list[NoteReadModel],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def get_opportunity_notes(
    op_query_use_case: Annotated[OpportunityQueryUseCase, Depends(get_op_query_use_case)],
    opportunity_id: Annotated[str, Path],
) -> None:
    try:
        notes = op_query_use_case.get_notes(opportunity_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return notes


@router.post(
    "/{opportunity_id}/notes",
    response_model=NoteReadModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def create_note(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: NoteCreateModel,
    opportunity_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        note = op_command_use_case.update_note(
            opportunity_id=opportunity_id, editor_id=current_user.salesman_id, note_data=data
        )
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return note

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, status

from building_blocks.application.exceptions import InvalidData, ObjectDoesNotExist, UnauthorizedAction
from customer_management.infrastructure.file import config as customer_file_config
from customer_management.infrastructure.file.customer.command import CustomerFileUnitOfWork
from sales.application.acl import CustomerService
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
from sales.infrastructure.file import config as file_config
from sales.infrastructure.file.opportunity.command import OpportunityFileUnitOfWork
from sales.infrastructure.file.opportunity.query_service import OpportunityFileQueryService
from sales.infrastructure.file.sales_representative.command import SalesRepresentativeFileUnitOfWork

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def get_op_query_use_case() -> OpportunityQueryUseCase:
    op_query_service = OpportunityFileQueryService()
    return OpportunityQueryUseCase(op_query_service)


def get_op_command_use_case() -> OpportunityCommandUseCase:
    customer_uow = CustomerFileUnitOfWork(customer_file_config.CUSTOMERS_FILE_PATH)
    salesman_uow = SalesRepresentativeFileUnitOfWork(file_config.SALES_REPR_FILE_PATH)
    customer_service = CustomerService(customer_uow=customer_uow)
    op_uow = OpportunityFileUnitOfWork(file_config.OPPORTUNITIES_FILE_PATH)
    return OpportunityCommandUseCase(
        opportunity_uow=op_uow, salesman_uow=salesman_uow, customer_service=customer_service
    )


@router.get("/", response_model=list[OpportunityReadModel])
def get_opportunities(
    op_query_use_case: Annotated[OpportunityQueryUseCase, Depends(get_op_query_use_case)],
    customer_id: str | None = None,
    owner_id: str | None = None,
    stage: str | None = None,
    priority: str | None = None,
) -> None:
    opportunities = op_query_use_case.get_filtered(
        customer_id=customer_id, owner_id=owner_id, stage=stage, priority=priority
    )
    return opportunities


@router.post("/", response_model=OpportunityReadModel)
def create_opportunity(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: OpportunityCreateModel,
) -> None:
    try:
        opportunity = op_command_use_case.create(data=data, creator_id=str(uuid4()))
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return opportunity


@router.get("/{opportunity_id}", response_model=OpportunityReadModel)
def get_single_opportunity(
    op_query_use_case: Annotated[OpportunityQueryUseCase, Depends(get_op_query_use_case)],
    opportunity_id: Annotated[str, Path],
) -> None:
    try:
        opportunity = op_query_use_case.get(opportunity_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return opportunity


@router.put("/{opportunity_id}", response_model=OpportunityReadModel)
def update_opportunity(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: OpportunityUpdateModel,
    opportunity_id: Annotated[str, Path],
    editor_id: Annotated[str, Path],  # DOZMIANY wywalić!!!
) -> None:
    try:
        opportunity = op_command_use_case.update(opportunity_id=opportunity_id, editor_id=editor_id, data=data)
    except UnauthorizedAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return opportunity


@router.get(
    "/{opportunity_id}/offer-items",
    response_model=list[OfferItemReadModel],
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


@router.put("/{opportunity_id}/offer-items", response_model=list[OfferItemReadModel])
def update_opportunity_offer(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: list[OfferItemCreateUpdateModel],
    opportunity_id: Annotated[str, Path],
    editor_id: Annotated[str, Path],
) -> None:
    try:
        offer_items = op_command_use_case.update_offer(opportunity_id=opportunity_id, editor_id=editor_id, data=data)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except UnauthorizedAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    return offer_items


@router.get(
    "/{opportunity_id}/notes",
    response_model=list[NoteReadModel],
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


@router.post("/{opportunity_id}/notes", response_model=NoteReadModel)
def create_note(
    op_command_use_case: Annotated[OpportunityCommandUseCase, Depends(get_op_command_use_case)],
    data: NoteCreateModel,
    opportunity_id: Annotated[str, Path],
    creator_id: Annotated[str, Path],  # DOZMIANY wywalić!!!
) -> None:
    try:
        note = op_command_use_case.update_note(opportunity_id=opportunity_id, editor_id=creator_id, note_data=data)
    except UnauthorizedAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    return note

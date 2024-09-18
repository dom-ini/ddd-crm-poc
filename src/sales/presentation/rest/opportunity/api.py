from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status

from building_blocks.application.exceptions import ObjectDoesNotExist
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.query import OpportunityQueryUseCase
from sales.application.opportunity.query_model import (
    OfferItemReadModel,
    OpportunityReadModel,
)
from sales.infrastructure.file.opportunity.query_service import (
    OpportunityFileQueryService,
)


router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def get_op_query_use_case() -> OpportunityQueryUseCase:
    op_query_service = OpportunityFileQueryService()
    return OpportunityQueryUseCase(op_query_service)


@router.get("/", response_model=list[OpportunityReadModel])
def get_opportunities(
    op_query_use_case: Annotated[
        OpportunityQueryUseCase, Depends(get_op_query_use_case)
    ],
    customer_id: str | None = None,
    owner_id: str | None = None,
    stage: str | None = None,
    priority: str | None = None,
) -> None:
    opportunities = op_query_use_case.get_filtered(
        customer_id=customer_id, owner_id=owner_id, stage=stage, priority=priority
    )
    return opportunities


@router.get("/{opportunity_id}", response_model=OpportunityReadModel)
def get_single_opportunity(
    op_query_use_case: Annotated[
        OpportunityQueryUseCase, Depends(get_op_query_use_case)
    ],
    opportunity_id: Annotated[str, Path],
) -> None:
    try:
        opportunity = op_query_use_case.get(opportunity_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return opportunity


@router.get(
    "/{opportunity_id}/offer-items",
    response_model=list[OfferItemReadModel],
)
def get_opportunity_offer(
    op_query_use_case: Annotated[
        OpportunityQueryUseCase, Depends(get_op_query_use_case)
    ],
    opportunity_id: Annotated[str, Path],
) -> None:
    try:
        offer = op_query_use_case.get_offer(opportunity_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return offer


@router.get(
    "/{opportunity_id}/notes",
    response_model=list[NoteReadModel],
)
def get_opportunity_notes(
    op_query_use_case: Annotated[
        OpportunityQueryUseCase, Depends(get_op_query_use_case)
    ],
    opportunity_id: Annotated[str, Path],
) -> None:
    try:
        notes = op_query_use_case.get_notes(opportunity_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return notes

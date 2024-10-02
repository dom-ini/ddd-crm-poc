from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from building_blocks.application.exceptions import ForbiddenAction, ObjectDoesNotExist
from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.application.sales_representative.command_model import (
    SalesRepresentativeCreateModel,
    SalesRepresentativeUpdateModel,
)
from sales.application.sales_representative.query import SalesRepresentativeQueryUseCase
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.presentation.container import get_container

router = APIRouter(prefix="/sales-representatives", tags=["sales representatives"])


def get_sr_query_use_case(request: Request) -> SalesRepresentativeQueryUseCase:
    container = get_container(request)
    return container.sr_query_use_case


def get_sr_command_use_case(request: Request) -> SalesRepresentativeCommandUseCase:
    container = get_container(request)
    return container.sr_command_use_case


@router.get("/", response_model=list[SalesRepresentativeReadModel])
def get_sales_representatives(
    sr_query_use_case: Annotated[SalesRepresentativeQueryUseCase, Depends(get_sr_query_use_case)],
) -> None:
    representatives = sr_query_use_case.get_all()
    return representatives


@router.post("/", response_model=SalesRepresentativeReadModel)
def create_sales_representative(
    sr_command_use_case: Annotated[SalesRepresentativeCommandUseCase, Depends(get_sr_command_use_case)],
    data: SalesRepresentativeCreateModel,
) -> None:
    representative = sr_command_use_case.create(data)
    return representative


@router.put("/", response_model=SalesRepresentativeReadModel)
def update_sales_representative(
    sr_command_use_case: Annotated[SalesRepresentativeCommandUseCase, Depends(get_sr_command_use_case)],
    representative_id: Annotated[str, Path],
    data: SalesRepresentativeUpdateModel,
    editor_id: Annotated[str, Path],  # DOZMIANY wywalić!!!
) -> None:
    try:
        representative = sr_command_use_case.update(representative_id=representative_id, editor_id=editor_id, data=data)
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return representative

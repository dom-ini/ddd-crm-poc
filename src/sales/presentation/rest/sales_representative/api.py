from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from authentication.infrastructure.exceptions import AuthenticationServiceFailed, InvalidUserCreationData
from authentication.infrastructure.service.base import AuthenticationService, UserCreateModel, UserReadModel
from authentication.presentation.rest.deps import get_auth_service, get_current_user, is_admin
from building_blocks.application.exceptions import ForbiddenAction, ObjectDoesNotExist
from building_blocks.presentation.responses import BasicErrorResponse, UnprocessableEntityResponse
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


@router.get("/", response_model=list[SalesRepresentativeReadModel], dependencies=[Depends(is_admin)])
def get_sales_representatives(
    sr_query_use_case: Annotated[SalesRepresentativeQueryUseCase, Depends(get_sr_query_use_case)],
) -> None:
    """For admins only."""
    representatives = sr_query_use_case.get_all()
    return representatives


@router.post(
    "/",
    response_model=SalesRepresentativeReadModel,
    dependencies=[Depends(is_admin)],
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def create_sales_representative(
    sr_command_use_case: Annotated[SalesRepresentativeCommandUseCase, Depends(get_sr_command_use_case)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
    salesman_data: SalesRepresentativeCreateModel,
    user_data: UserCreateModel,
) -> None:
    """For admins only."""
    representative = sr_command_use_case.create(salesman_data)
    try:
        auth_service.create_account(email=user_data.email, salesman_id=representative.id)
    except InvalidUserCreationData as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except AuthenticationServiceFailed as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message) from e
    return representative


@router.put(
    "/{representative_id}",
    response_model=SalesRepresentativeReadModel,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def update_sales_representative(
    sr_command_use_case: Annotated[SalesRepresentativeCommandUseCase, Depends(get_sr_command_use_case)],
    representative_id: Annotated[str, Path],
    data: SalesRepresentativeUpdateModel,
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        representative = sr_command_use_case.update(
            representative_id=representative_id, editor_id=current_user.salesman_id, data=data
        )
    except ForbiddenAction as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    return representative

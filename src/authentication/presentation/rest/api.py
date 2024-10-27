from typing import Annotated

from fastapi import APIRouter, Depends, status

from authentication.infrastructure.service.base import UserReadModel
from authentication.presentation.rest.deps import get_current_user
from building_blocks.presentation.responses import BasicErrorResponse

router = APIRouter(
    prefix="/auth", tags=["authentication"], responses={status.HTTP_401_UNAUTHORIZED: {"model": BasicErrorResponse}}
)


@router.get(
    "/users/me",
    response_model=UserReadModel,
    responses={status.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse, "description": "Disabled account"}},
)
def get_current_user_data(user: Annotated[UserReadModel, Depends(get_current_user)]) -> None:
    return user

from typing import Annotated

from fastapi import APIRouter, Depends

from authentication.infrastructure.service.base import UserReadModel
from authentication.presentation.rest.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/users/me", response_model=UserReadModel)
def get_current_user(user: Annotated[UserReadModel, Depends(get_current_user)]) -> None:
    return user

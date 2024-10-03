from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from authentication.infrastructure.exceptions import AccountDisabled, InvalidToken
from authentication.infrastructure.roles import UserRole
from authentication.infrastructure.service.base import AuthenticationService, UserReadModel
from authentication.presentation.container import get_container
from building_blocks.infrastructure.exceptions import ServerError

security = HTTPBearer(auto_error=False)


def get_auth_service(request: Request) -> AuthenticationService:
    container = get_container(request)
    return container.auth_service


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> UserReadModel:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = credentials.credentials
    try:
        user_data = auth_service.verify_token(token)
    except InvalidToken as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message) from e
    except AccountDisabled as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ServerError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message) from e
    return user_data


def is_admin(
    user_data: Annotated[UserReadModel, Depends(get_current_user)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> bool:
    if not auth_service.has_role(user_data=user_data, role=UserRole.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have required permissions",
        )

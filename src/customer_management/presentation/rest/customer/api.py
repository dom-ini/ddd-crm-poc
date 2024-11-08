from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status as status_code

from authentication.infrastructure.service.base import UserReadModel
from authentication.presentation.rest.deps import get_current_user
from building_blocks.application.exceptions import ConflictingAction, ForbiddenAction, InvalidData, ObjectDoesNotExist
from building_blocks.infrastructure.exceptions import ServerError
from building_blocks.presentation.responses import BasicErrorResponse, UnprocessableEntityResponse
from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.command_model import (
    ContactPersonCreateModel,
    ContactPersonUpdateModel,
    CustomerCreateModel,
    CustomerUpdateModel,
)
from customer_management.application.query import CustomerQueryUseCase
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.domain.value_objects.company_segment import CompanySize, LegalForm
from customer_management.domain.value_objects.customer_status import CustomerStatusName
from customer_management.domain.value_objects.industry import IndustryName
from customer_management.presentation.container import get_container

router = APIRouter(prefix="/customers", tags=["customers"], dependencies=[Depends(get_current_user)])


def get_customer_query_use_case(request: Request) -> CustomerQueryUseCase:
    container = get_container(request)
    return container.customer_query_use_case


def get_customer_command_use_case(request: Request) -> CustomerCommandUseCase:
    container = get_container(request)
    return container.customer_command_use_case


@router.get(
    "/",
    response_model=list[CustomerReadModel],
)
def get_customers(
    customer_query_use_case: Annotated[CustomerQueryUseCase, Depends(get_customer_query_use_case)],
    relation_manager_id: str | None = None,
    status: CustomerStatusName | None = None,
    company_name: str | None = None,
    industry: IndustryName | None = None,
    company_size: CompanySize | None = None,
    legal_form: LegalForm | None = None,
) -> None:
    customers = customer_query_use_case.get_filtered(
        relation_manager_id=relation_manager_id,
        status=status,
        company_name=company_name,
        industry=industry,
        company_size=company_size,
        legal_form=legal_form,
    )
    return customers


@router.post(
    "/",
    response_model=CustomerReadModel,
    responses={status_code.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse}},
)
def create_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: CustomerCreateModel,
) -> None:
    try:
        customer = customer_command_use_case.create(customer_data=data)
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return customer


@router.put(
    "/{customer_id}",
    response_model=CustomerReadModel,
    responses={
        status_code.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status_code.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def update_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: CustomerUpdateModel,
    customer_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        customer = customer_command_use_case.update(
            customer_id=customer_id, editor_id=current_user.salesman_id, customer_data=data
        )
    except ForbiddenAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    except ServerError as e:
        raise HTTPException(status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message) from e
    return customer


@router.get(
    "/{customer_id}",
    response_model=CustomerReadModel,
    responses={
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def get_single_customer(
    customer_query_use_case: Annotated[CustomerQueryUseCase, Depends(get_customer_query_use_case)],
    customer_id: Annotated[str, Path],
) -> None:
    try:
        customer = customer_query_use_case.get(customer_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    return customer


@router.post(
    "/{customer_id}/convert",
    status_code=status_code.HTTP_204_NO_CONTENT,
    responses={
        status_code.HTTP_400_BAD_REQUEST: {"model": UnprocessableEntityResponse},
        status_code.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status_code.HTTP_409_CONFLICT: {"model": BasicErrorResponse},
    },
)
def convert_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    customer_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        customer_command_use_case.convert(customer_id, requestor_id=current_user.salesman_id)
    except ConflictingAction as e:
        raise HTTPException(status_code=status_code.HTTP_409_CONFLICT, detail=e.message) from e
    except ForbiddenAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.post(
    "/{customer_id}/archive",
    status_code=status_code.HTTP_204_NO_CONTENT,
    responses={
        status_code.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status_code.HTTP_409_CONFLICT: {"model": BasicErrorResponse},
        status_code.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def archive_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    customer_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        customer_command_use_case.archive(customer_id, requestor_id=current_user.salesman_id)
    except ConflictingAction as e:
        raise HTTPException(status_code=status_code.HTTP_409_CONFLICT, detail=e.message) from e
    except ForbiddenAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.get(
    "/{customer_id}/contact-persons",
    response_model=list[ContactPersonReadModel],
    responses={
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def get_customers_contact_persons(
    customer_query_use_case: Annotated[CustomerQueryUseCase, Depends(get_customer_query_use_case)],
    customer_id: Annotated[str, Path],
) -> None:
    try:
        contact_persons = customer_query_use_case.get_contact_persons(customer_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    return contact_persons


@router.post(
    "/{customer_id}/contact-persons",
    response_model=ContactPersonReadModel,
    responses={
        status_code.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status_code.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def create_customers_contact_person(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: ContactPersonCreateModel,
    customer_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        contact_person = customer_command_use_case.create_contact_person(
            customer_id=customer_id, editor_id=current_user.salesman_id, data=data
        )
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ForbiddenAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    return contact_person


@router.put(
    "/{customer_id}/contact-persons/{contact_person_id}",
    response_model=ContactPersonReadModel,
    responses={
        status_code.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
        status_code.HTTP_422_UNPROCESSABLE_ENTITY: {"model": UnprocessableEntityResponse},
    },
)
def update_customers_contact_person(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: ContactPersonUpdateModel,
    customer_id: Annotated[str, Path],
    contact_person_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        contact_person = customer_command_use_case.update_contact_person(
            customer_id=customer_id, contact_person_id=contact_person_id, editor_id=current_user.salesman_id, data=data
        )
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ForbiddenAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    return contact_person


@router.delete(
    "/{customer_id}/contact-persons/{contact_person_id}",
    status_code=status_code.HTTP_204_NO_CONTENT,
    responses={
        status_code.HTTP_403_FORBIDDEN: {"model": BasicErrorResponse},
        status_code.HTTP_404_NOT_FOUND: {"model": BasicErrorResponse},
    },
)
def remove_customers_contact_person(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    customer_id: Annotated[str, Path],
    contact_person_id: Annotated[str, Path],
    current_user: Annotated[UserReadModel, Depends(get_current_user)],
) -> None:
    try:
        customer_command_use_case.remove_contact_person(
            customer_id=customer_id, contact_person_id=contact_person_id, editor_id=current_user.salesman_id
        )
    except ForbiddenAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status as status_code

from building_blocks.application.exceptions import ConfictingAction, InvalidData, ObjectDoesNotExist, UnauthorizedAction
from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.command_model import (
    ContactPersonCreateModel,
    ContactPersonUpdateModel,
    CustomerCreateModel,
    CustomerUpdateModel,
)
from customer_management.application.query import CustomerQueryUseCase
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.infrastructure.file import config as file_config
from customer_management.infrastructure.file.customer.command import CustomerFileUnitOfWork
from customer_management.infrastructure.file.customer.query_service import CustomerFileQueryService

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_query_use_case() -> CustomerQueryUseCase:
    customer_query_service = CustomerFileQueryService()
    return CustomerQueryUseCase(customer_query_service)


def get_customer_command_use_case() -> CustomerCommandUseCase:
    customer_uow = CustomerFileUnitOfWork(file_config.CUSTOMERS_FILE_PATH)
    return CustomerCommandUseCase(customer_uow)


@router.get(
    "/",
    response_model=list[CustomerReadModel],
)
def get_customers(
    customer_query_use_case: Annotated[CustomerQueryUseCase, Depends(get_customer_query_use_case)],
    relation_manager_id: str | None = None,
    status: str | None = None,
    company_name: str | None = None,
    industry: str | None = None,
    company_size: str | None = None,
    legal_form: str | None = None,
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


@router.post("/", response_model=CustomerReadModel)
def create_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: CustomerCreateModel,
) -> None:
    try:
        customer = customer_command_use_case.create(customer_data=data)
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return customer


@router.put("/{customer_id}", response_model=CustomerReadModel)
def update_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: CustomerUpdateModel,
    customer_id: Annotated[str, Path],
    editor_id: Annotated[str, Path],  # DOZMIANY wywalić!!
) -> None:
    try:
        customer = customer_command_use_case.update(customer_id=customer_id, editor_id=editor_id, customer_data=data)
    except UnauthorizedAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    return customer


@router.get(
    "/{customer_id}",
    response_model=CustomerReadModel,
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
)
def convert_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    customer_id: Annotated[str, Path],
    requestor_id: Annotated[str, Path],  # DOZMIANY wywalić!!
) -> None:
    try:
        customer_command_use_case.convert(customer_id, requestor_id=requestor_id)
    except ConfictingAction as e:
        raise HTTPException(status_code=status_code.HTTP_409_CONFLICT, detail=e.message) from e
    except UnauthorizedAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_400_BAD_REQUEST, detail=e.message) from e


@router.post(
    "/{customer_id}/archive",
    status_code=status_code.HTTP_204_NO_CONTENT,
)
def archive_customer(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    customer_id: Annotated[str, Path],
    requestor_id: Annotated[str, Path],  # DOZMIANY wywalić!!
) -> None:
    try:
        customer_command_use_case.archive(customer_id, requestor_id=requestor_id)
    except ConfictingAction as e:
        raise HTTPException(status_code=status_code.HTTP_409_CONFLICT, detail=e.message) from e
    except UnauthorizedAction as e:
        raise HTTPException(status_code=status_code.HTTP_403_FORBIDDEN, detail=e.message) from e


@router.get(
    "/{customer_id}/contact-persons",
    response_model=list[ContactPersonReadModel],
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
)
def create_customers_contact_person(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: ContactPersonCreateModel,
    customer_id: Annotated[str, Path],
) -> None:
    try:
        contact_person = customer_command_use_case.create_contact_person(customer_id=customer_id, data=data)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return contact_person


@router.put(
    "/{customer_id}/contact-persons/{contact_person_id}",
    response_model=ContactPersonReadModel,
)
def update_customers_contact_person(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    data: ContactPersonUpdateModel,
    customer_id: Annotated[str, Path],
    contact_person_id: Annotated[str, Path],
) -> None:
    try:
        contact_person = customer_command_use_case.update_contact_person(
            customer_id=customer_id, contact_person_id=contact_person_id, data=data
        )
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e
    except InvalidData as e:
        raise HTTPException(status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    return contact_person


@router.delete(
    "/{customer_id}/contact-persons/{contact_person_id}",
    status_code=status_code.HTTP_204_NO_CONTENT,
)
def remove_customers_contact_person(
    customer_command_use_case: Annotated[CustomerCommandUseCase, Depends(get_customer_command_use_case)],
    customer_id: Annotated[str, Path],
    contact_person_id: Annotated[str, Path],
) -> None:
    try:
        customer_command_use_case.remove_contact_person(customer_id=customer_id, contact_person_id=contact_person_id)
    except ObjectDoesNotExist as e:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND, detail=e.message) from e

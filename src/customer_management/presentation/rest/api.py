from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status

from customer_management.application.query_model import (
    ContactPersonReadModel,
    CustomerReadModel,
)
from customer_management.application.query import CustomerQueryUseCase
from customer_management.infrastructure.file.customer.query_service import (
    CustomerFileQueryService,
)
from customer_management.application.exceptions import CustomerDoesNotExist


router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_query_use_case() -> CustomerQueryUseCase:
    customer_query_service = CustomerFileQueryService()
    return CustomerQueryUseCase(customer_query_service)


@router.get(
    "/",
    response_model=list[CustomerReadModel],
)
def get_customers(
    customer_query_usecase: Annotated[
        CustomerQueryUseCase, Depends(get_customer_query_use_case)
    ],
    relation_manager_id: str | None = None,
    status: str | None = None,
    company_name: str | None = None,
    industry: str | None = None,
    company_size: str | None = None,
    legal_form: str | None = None,
) -> None:
    customers = customer_query_usecase.get_filtered(
        relation_manager_id=relation_manager_id,
        status=status,
        company_name=company_name,
        industry=industry,
        company_size=company_size,
        legal_form=legal_form,
    )
    return customers


@router.get(
    "/{customer_id}",
    response_model=CustomerReadModel,
)
def get_single_customer(
    customer_query_usecase: Annotated[
        CustomerQueryUseCase, Depends(get_customer_query_use_case)
    ],
    customer_id: Annotated[str, Path],
) -> None:
    try:
        customer = customer_query_usecase.get(customer_id)
    except CustomerDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return customer


@router.get(
    "/{customer_id}/contact-persons",
    response_model=list[ContactPersonReadModel],
)
def get_customers_contact_persons(
    customer_query_usecase: Annotated[
        CustomerQueryUseCase, Depends(get_customer_query_use_case)
    ],
    customer_id: Annotated[str, Path],
) -> None:
    try:
        contact_persons = customer_query_usecase.get_contact_persons(customer_id)
    except CustomerDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    return contact_persons

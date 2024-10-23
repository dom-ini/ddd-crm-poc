from typing import Annotated

from fastapi import APIRouter, Depends, Request

from authentication.presentation.rest.deps import get_current_user
from building_blocks.infrastructure.vo_service import ValueObjectService
from sales.application.opportunity.query_model import CurrencyReadModel, ProductReadModel
from sales.presentation.container import get_container

router = APIRouter(tags=["value objects"], dependencies=[Depends(get_current_user)])


def get_currency_vo_service(request: Request) -> ValueObjectService:
    container = get_container(request)
    return container.currency_vo_service


def get_product_vo_service(request: Request) -> ValueObjectService:
    container = get_container(request)
    return container.product_vo_service


@router.get("/currencies", response_model=list[CurrencyReadModel])
def get_currencies(currency_vo_service: Annotated[ValueObjectService, Depends(get_currency_vo_service)]) -> None:
    currencies = currency_vo_service.get_all()
    return currencies


@router.get("/products", response_model=list[ProductReadModel])
def get_products(product_vo_service: Annotated[ValueObjectService, Depends(get_product_vo_service)]) -> None:
    products = product_vo_service.get_all()
    return products

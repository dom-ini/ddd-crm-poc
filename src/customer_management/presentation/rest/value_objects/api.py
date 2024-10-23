from typing import Annotated

from fastapi import APIRouter, Depends, Request

from authentication.presentation.rest.deps import get_current_user
from building_blocks.infrastructure.vo_service import ValueObjectService
from customer_management.application.query_model import CountryReadModel, LanguageReadModel
from customer_management.presentation.container import get_container

router = APIRouter(tags=["value objects"], dependencies=[Depends(get_current_user)])


def get_country_vo_service(request: Request) -> ValueObjectService:
    container = get_container(request)
    return container.country_vo_service


def get_language_vo_service(request: Request) -> ValueObjectService:
    container = get_container(request)
    return container.language_vo_service


@router.get("/countries", response_model=list[CountryReadModel])
def get_countries(country_vo_service: Annotated[ValueObjectService, Depends(get_country_vo_service)]) -> None:
    countries = country_vo_service.get_all()
    return countries


@router.get("/languages", response_model=list[LanguageReadModel])
def get_languages(language_vo_service: Annotated[ValueObjectService, Depends(get_language_vo_service)]) -> None:
    languages = language_vo_service.get_all()
    return languages

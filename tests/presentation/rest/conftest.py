from collections.abc import Callable, Iterator
from typing import ContextManager
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from authentication.infrastructure.service.base import UserReadModel
from authentication.infrastructure.service.firebase import FirebaseAuthenticationService, FirebaseUserReadModel
from building_blocks.infrastructure.sql.vo_service import SQLValueObjectService
from containers.container import ApplicationContainer
from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.query_model import CountryReadModel, LanguageReadModel
from customer_management.infrastructure.sql.customer.command import CustomerSQLUnitOfWork
from customer_management.infrastructure.sql.customer.models import CountryModel, LanguageModel
from customer_management.infrastructure.sql.customer.query_service import CustomerSQLQueryService
from entrypoints.rest import app as main_app, bind_container
from sales.application.acl import CustomerService
from sales.application.lead.command import LeadCommandUseCase
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.opportunity.query_model import CurrencyReadModel, ProductReadModel
from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.infrastructure.sql.lead.command import LeadSQLUnitOfWork
from sales.infrastructure.sql.lead.query_service import LeadSQLQueryService
from sales.infrastructure.sql.opportunity.command import OpportunitySQLUnitOfWork
from sales.infrastructure.sql.opportunity.models import CurrencyModel, ProductModel
from sales.infrastructure.sql.opportunity.query_service import OpportunitySQLQueryService
from sales.infrastructure.sql.sales_representative.command import SalesRepresentativeSQLUnitOfWork
from sales.infrastructure.sql.sales_representative.query_service import SalesRepresentativeSQLQueryService


class TestingContainer(ApplicationContainer):
    def __init__(self, session_factory: Callable[[], ContextManager[Session]], user_data: UserReadModel) -> None:
        self._auth_service = MagicMock(spec=FirebaseAuthenticationService)
        self._auth_service.verify_token.return_value = FirebaseUserReadModel.from_token_data(user_data)
        self._auth_service.has_role.return_value = False

        self._customer_uow = CustomerSQLUnitOfWork(session_factory)
        self._lead_uow = LeadSQLUnitOfWork(session_factory)
        self._opportunity_uow = OpportunitySQLUnitOfWork(session_factory)
        self._sr_uow = SalesRepresentativeSQLUnitOfWork(session_factory)

        self._customer_service = CustomerService(customer_uow=self._customer_uow)
        self._sr_service = SalesRepresentativeService(salesman_uow=self._sr_uow)
        self._opportunity_service = OpportunityService(opportunity_uow=self._opportunity_uow)

        self._customer_qs = CustomerSQLQueryService(session_factory)
        self._lead_qs = LeadSQLQueryService(session_factory)
        self._opportunity_qs = OpportunitySQLQueryService(session_factory)
        self._sr_qs = SalesRepresentativeSQLQueryService(session_factory)

        self.language_vo_service = SQLValueObjectService(
            session_factory=session_factory, model=LanguageModel, read_model=LanguageReadModel
        )
        self.country_vo_service = SQLValueObjectService(
            session_factory=session_factory, model=CountryModel, read_model=CountryReadModel
        )
        self.currency_vo_service = SQLValueObjectService(
            session_factory=session_factory, model=CurrencyModel, read_model=CurrencyReadModel
        )
        self.product_vo_service = SQLValueObjectService(
            session_factory=session_factory, model=ProductModel, read_model=ProductReadModel
        )


@pytest.fixture(scope="session")
def user_data() -> dict:
    return {"uid": "user id", "salesman_id": "salesman id", "roles": []}


@pytest.fixture(scope="session")
def user(user_data: dict) -> UserReadModel:
    return FirebaseUserReadModel.from_token_data(user_data)


@pytest.fixture(scope="session")
def testing_container(session_factory: Callable[[], ContextManager[Session]], user_data: dict) -> ApplicationContainer:
    return TestingContainer(session_factory, user_data)


@pytest.fixture(scope="session")
def auth_headers() -> dict:
    return {"Authorization": "Bearer some token"}


@pytest.fixture(scope="session")
def mock_auth_service(testing_container: ApplicationContainer) -> MagicMock:
    return testing_container.auth_service


@pytest.fixture(scope="session")
def customer_command_use_case(testing_container: ApplicationContainer) -> CustomerCommandUseCase:
    return testing_container.customer_command_use_case


@pytest.fixture(scope="session")
def sr_command_use_case(testing_container: ApplicationContainer) -> SalesRepresentativeCommandUseCase:
    return testing_container.sr_command_use_case


@pytest.fixture(scope="session")
def opportunity_command_use_case(testing_container: ApplicationContainer) -> OpportunityCommandUseCase:
    return testing_container.opportunity_command_use_case


@pytest.fixture(scope="session")
def lead_command_use_case(testing_container: ApplicationContainer) -> LeadCommandUseCase:
    return testing_container.lead_command_use_case


@pytest.fixture()
def change_user_salesman_id(
    mock_auth_service: MagicMock,
    representative_3: SalesRepresentativeReadModel,
) -> Iterator[None]:
    old_user = mock_auth_service.verify_token.return_value
    new_user = FirebaseUserReadModel.from_token_data(
        {"uid": "some id", "salesman_id": representative_3.id, "roles": []}
    )
    mock_auth_service.verify_token.return_value = new_user
    yield
    mock_auth_service.verify_token.return_value = old_user


@pytest.fixture()
def set_user_admin(mock_auth_service: MagicMock) -> Iterator[None]:
    mock_auth_service.has_role.return_value = True
    yield
    mock_auth_service.has_role.return_value = False


@pytest.fixture(scope="session")
def client(testing_container: ApplicationContainer, auth_headers: dict) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(main_app.router)
    bind_container(app, testing_container)

    client = TestClient(app, headers=auth_headers)
    yield client

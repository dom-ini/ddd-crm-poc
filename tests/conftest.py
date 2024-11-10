from collections.abc import Callable
from typing import ContextManager
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from authentication.infrastructure.service.base import UserReadModel
from authentication.infrastructure.service.firebase import FirebaseAuthenticationService, FirebaseUserReadModel
from building_blocks.infrastructure.sql.vo_service import SQLValueObjectService
from containers.container import ApplicationContainer
from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.command_model import (
    CompanyInfoCreateUpdateModel,
    ContactMethodCreateUpdateModel,
    ContactPersonCreateModel,
    CustomerCreateModel,
    LanguageCreateUpdateModel,
)
from customer_management.application.query_model import CountryReadModel, CustomerReadModel, LanguageReadModel
from customer_management.domain.value_objects.language import Language
from customer_management.infrastructure.sql.customer.command import CustomerSQLUnitOfWork
from customer_management.infrastructure.sql.customer.models import CountryModel, LanguageModel
from customer_management.infrastructure.sql.customer.query_service import CustomerSQLQueryService
from sales.application.acl import CustomerService
from sales.application.lead.command import LeadCommandUseCase
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.opportunity.command_model import OfferItemCreateUpdateModel, OpportunityCreateModel
from sales.application.opportunity.query_model import CurrencyReadModel, OpportunityReadModel, ProductReadModel
from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.infrastructure.sql.lead.command import LeadSQLUnitOfWork
from sales.infrastructure.sql.lead.query_service import LeadSQLQueryService
from sales.infrastructure.sql.opportunity.command import OpportunitySQLUnitOfWork
from sales.infrastructure.sql.opportunity.models import CurrencyModel, ProductModel
from sales.infrastructure.sql.opportunity.query_service import OpportunitySQLQueryService
from sales.infrastructure.sql.sales_representative.command import SalesRepresentativeSQLUnitOfWork
from sales.infrastructure.sql.sales_representative.query_service import SalesRepresentativeSQLQueryService
from tests.fixtures.sql.data_fixtures import (
    address,
    company_info,
    contact_person,
    country,
    create_value_objects_in_db,
    currency,
    customer_1,
    customer_2,
    customer_3,
    customer_4,
    language,
    lead_1,
    lead_2,
    note_content,
    offer_item,
    opportunity_1,
    opportunity_2,
    opportunity_3,
    product_1,
    product_2,
    representative_1,
    representative_2,
    representative_3,
)
from tests.fixtures.sql.db_fixtures import clear_sql_test_data, connection_manager, run_migrations, session_factory


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
def testing_container(session_factory: Callable[[], ContextManager[Session]], user_data: dict) -> ApplicationContainer:
    return TestingContainer(session_factory, user_data)


@pytest.fixture(scope="session")
def user_data() -> dict:
    return {"uid": "user id", "salesman_id": "salesman id", "roles": []}


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


@pytest.fixture(scope="session")
def api_customer_with_open_opportunity(
    customer_command_use_case: CustomerCommandUseCase,
    company_info: CompanyInfoCreateUpdateModel,
    representative_3: SalesRepresentativeReadModel,
    language: Language,
) -> CustomerReadModel:
    data = CustomerCreateModel(relation_manager_id=representative_3.id, company_info=company_info)
    customer = customer_command_use_case.create(customer_data=data)
    contact_person_data = ContactPersonCreateModel(
        first_name="Jan",
        last_name="Kowalski",
        job_title="CFO",
        preferred_language=LanguageCreateUpdateModel(name=language.name, code=language.code),
        contact_methods=(
            (
                ContactMethodCreateUpdateModel(
                    type="email", value="apicustomerwithopportunity@example.com", is_preferred=True
                )
            ),
        ),
    )
    customer_command_use_case.create_contact_person(
        customer_id=customer.id,
        editor_id=customer.relation_manager_id,
        data=contact_person_data,
    )
    customer_command_use_case.convert(customer_id=customer.id, requestor_id=customer.relation_manager_id)
    return customer


@pytest.fixture(scope="session")
def api_opportunity(
    api_customer_with_open_opportunity: CustomerReadModel,
    opportunity_command_use_case: OpportunityCommandUseCase,
    offer_item: OfferItemCreateUpdateModel,
) -> OpportunityReadModel:
    data = OpportunityCreateModel(
        customer_id=api_customer_with_open_opportunity.id, source="ads", priority="low", offer=(offer_item,)
    )
    opportunity = opportunity_command_use_case.create(
        data=data, creator_id=api_customer_with_open_opportunity.relation_manager_id
    )
    return opportunity

from collections.abc import Callable, Iterator
from typing import ContextManager

import pytest
from sqlalchemy.orm import Session

from building_blocks.infrastructure.sql.db import DbConnectionManager
from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.application.command import CustomerCommandUseCase
from customer_management.infrastructure.sql.customer.command import CustomerSQLUnitOfWork
from sales.application.acl import CustomerService, ICustomerService
from sales.application.lead.command import LeadCommandUseCase
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.infrastructure.sql.lead.command import LeadSQLUnitOfWork
from sales.infrastructure.sql.opportunity.command import OpportunitySQLUnitOfWork
from sales.infrastructure.sql.sales_representative.command import SalesRepresentativeSQLUnitOfWork
from tests.fixtures.sql.db_fixtures import SQL_TEST_DB_URL


@pytest.fixture(name="session")
def one_off_session() -> Iterator[Session]:
    factory = DbConnectionManager.get_session_factory(SQL_TEST_DB_URL)
    with factory() as db:
        yield db
    DbConnectionManager._engine.dispose()


@pytest.fixture(scope="session")
def customer_service(session_factory: Callable[[], ContextManager[Session]]) -> ICustomerService:
    customer_uow = CustomerSQLUnitOfWork(session_factory)
    return CustomerService(customer_uow=customer_uow)


@pytest.fixture(scope="session")
def sr_uow(session_factory: Callable[[], ContextManager[Session]]) -> SalesRepresentativeSQLUnitOfWork:
    return SalesRepresentativeSQLUnitOfWork(session_factory)


@pytest.fixture(scope="session")
def opportunity_uow(session_factory: Callable[[], ContextManager[Session]]) -> OpportunitySQLUnitOfWork:
    return OpportunitySQLUnitOfWork(session_factory)


@pytest.fixture(scope="session")
def sr_command_use_case(
    sr_uow: SalesRepresentativeSQLUnitOfWork,
) -> SalesRepresentativeCommandUseCase:
    command_use_case = SalesRepresentativeCommandUseCase(sr_uow=sr_uow)
    return command_use_case


@pytest.fixture(scope="session")
def lead_command_use_case(
    customer_service: ICustomerService,
    sr_uow: SalesRepresentativeSQLUnitOfWork,
    session_factory: Callable[[], ContextManager[Session]],
) -> LeadCommandUseCase:
    uow = LeadSQLUnitOfWork(session_factory)
    command_use_case = LeadCommandUseCase(lead_uow=uow, salesman_uow=sr_uow, customer_service=customer_service)
    return command_use_case


@pytest.fixture(scope="session")
def opportunity_command_use_case(
    customer_service: ICustomerService,
    sr_uow: SalesRepresentativeSQLUnitOfWork,
    opportunity_uow: OpportunitySQLUnitOfWork,
) -> OpportunityCommandUseCase:
    command_use_case = OpportunityCommandUseCase(
        opportunity_uow=opportunity_uow,
        salesman_uow=sr_uow,
        customer_service=customer_service,
    )
    return command_use_case


@pytest.fixture(scope="session")
def customer_command_use_case(
    sr_uow: SalesRepresentativeSQLUnitOfWork,
    opportunity_uow: OpportunitySQLUnitOfWork,
    session_factory: Callable[[], ContextManager[Session]],
) -> CustomerCommandUseCase:
    sales_rep_service = SalesRepresentativeService(salesman_uow=sr_uow)
    opportunity_service = OpportunityService(opportunity_uow=opportunity_uow)
    uow = CustomerSQLUnitOfWork(session_factory)
    command_use_case = CustomerCommandUseCase(
        customer_uow=uow,
        sales_rep_service=sales_rep_service,
        opportunity_service=opportunity_service,
    )
    return command_use_case

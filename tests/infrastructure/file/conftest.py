import pytest

from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.application.command import CustomerCommandUseCase
from customer_management.infrastructure.file.customer.command import CustomerFileUnitOfWork
from sales.application.acl import CustomerService, ICustomerService
from sales.application.lead.command import LeadCommandUseCase
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.infrastructure.file.lead.command import LeadFileUnitOfWork
from sales.infrastructure.file.opportunity.command import OpportunityFileUnitOfWork
from sales.infrastructure.file.sales_representative.command import SalesRepresentativeFileUnitOfWork
from tests.fixtures.file.data_fixtures import (
    address,
    company_info,
    contact_person,
    customer_1,
    customer_2,
    customer_3,
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
from tests.fixtures.file.db_fixtures import (
    FILE_CUSTOMER_TEST_DATA_PATH,
    FILE_LEAD_TEST_DATA_PATH,
    FILE_OPPORTUNITY_TEST_DATA_PATH,
    FILE_SALES_REPRESENTATIVE_TEST_DATA_PATH,
    clear_file_test_data,
)


@pytest.fixture(scope="session")
def customer_service() -> ICustomerService:
    customer_uow = CustomerFileUnitOfWork(FILE_CUSTOMER_TEST_DATA_PATH)
    return CustomerService(customer_uow=customer_uow)


@pytest.fixture(scope="session")
def sr_uow() -> SalesRepresentativeFileUnitOfWork:
    return SalesRepresentativeFileUnitOfWork(FILE_SALES_REPRESENTATIVE_TEST_DATA_PATH)


@pytest.fixture(scope="session")
def opportunity_uow() -> OpportunityFileUnitOfWork:
    return OpportunityFileUnitOfWork(FILE_OPPORTUNITY_TEST_DATA_PATH)


@pytest.fixture(scope="session")
def sr_command_use_case(
    sr_uow: SalesRepresentativeFileUnitOfWork,
) -> SalesRepresentativeCommandUseCase:
    command_use_case = SalesRepresentativeCommandUseCase(sr_uow=sr_uow)
    return command_use_case


@pytest.fixture(scope="session")
def lead_command_use_case(
    customer_service: ICustomerService, sr_uow: SalesRepresentativeFileUnitOfWork
) -> LeadCommandUseCase:
    uow = LeadFileUnitOfWork(FILE_LEAD_TEST_DATA_PATH)
    command_use_case = LeadCommandUseCase(lead_uow=uow, salesman_uow=sr_uow, customer_service=customer_service)
    return command_use_case


@pytest.fixture(scope="session")
def opportunity_command_use_case(
    customer_service: ICustomerService,
    sr_uow: SalesRepresentativeFileUnitOfWork,
    opportunity_uow: OpportunityFileUnitOfWork,
) -> OpportunityCommandUseCase:
    command_use_case = OpportunityCommandUseCase(
        opportunity_uow=opportunity_uow,
        salesman_uow=sr_uow,
        customer_service=customer_service,
    )
    return command_use_case


@pytest.fixture(scope="session")
def customer_command_use_case(
    sr_uow: SalesRepresentativeFileUnitOfWork,
    opportunity_uow: OpportunityFileUnitOfWork,
) -> CustomerCommandUseCase:
    sales_rep_service = SalesRepresentativeService(salesman_uow=sr_uow)
    opportunity_service = OpportunityService(opportunity_uow=opportunity_uow)
    uow = CustomerFileUnitOfWork(FILE_CUSTOMER_TEST_DATA_PATH)
    command_use_case = CustomerCommandUseCase(
        customer_uow=uow,
        sales_rep_service=sales_rep_service,
        opportunity_service=opportunity_service,
    )
    return command_use_case

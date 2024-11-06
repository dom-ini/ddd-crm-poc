import pytest

from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.command_model import (
    CompanyInfoCreateUpdateModel,
    ContactMethodCreateUpdateModel,
    ContactPersonCreateModel,
    CustomerCreateModel,
    LanguageCreateUpdateModel,
)
from customer_management.application.query_model import CustomerReadModel
from customer_management.domain.value_objects.language import Language
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.opportunity.command_model import OfferItemCreateUpdateModel, OpportunityCreateModel
from sales.application.opportunity.query_model import OpportunityReadModel
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
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

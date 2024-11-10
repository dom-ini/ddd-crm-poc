import click

from building_blocks.presentation.cli.context import CliContext
from building_blocks.presentation.cli.data_processing import transform_data
from building_blocks.presentation.cli.renderer import get_headers_from_model
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.domain.value_objects.company_segment import ALLOWED_COMPANY_SIZES, ALLOWED_LEGAL_FORMS
from customer_management.domain.value_objects.customer_status import CustomerStatusName
from customer_management.domain.value_objects.industry import ALLOWED_INDUSTRY_NAMES
from customer_management.presentation.container import CustomerManagementApplicationContainer


@click.command()
@click.option("--relation-manager-id", type=click.STRING)
@click.option("--status", type=click.Choice(CustomerStatusName))
@click.option("--company-name", type=click.STRING)
@click.option("--industry", type=click.Choice(ALLOWED_INDUSTRY_NAMES))
@click.option("--company-size", type=click.Choice(ALLOWED_COMPANY_SIZES))
@click.option("--legal-form", type=click.Choice(ALLOWED_LEGAL_FORMS))
@click.pass_obj
def get_customers(
    context: CliContext[CustomerManagementApplicationContainer],
    relation_manager_id: str,
    status: str,
    company_name: str,
    industry: str,
    company_size: str,
    legal_form: str,
) -> None:
    customers = context.container.customer_query_use_case.get_filtered(
        relation_manager_id=relation_manager_id,
        status=status,
        company_name=company_name,
        industry=industry,
        company_size=company_size,
        legal_form=legal_form,
    )
    context.renderer.as_table(data=transform_data(customers), headers=get_headers_from_model(CustomerReadModel))


@click.command()
@click.argument("customer_id", type=click.STRING)
@click.pass_obj
def get_customer(context: CliContext[CustomerManagementApplicationContainer], customer_id: str) -> None:
    customer = context.container.customer_query_use_case.get(customer_id)
    context.renderer.as_table(data=transform_data([customer]), headers=get_headers_from_model(CustomerReadModel))


@click.command()
@click.argument("customer_id", type=click.STRING)
@click.pass_obj
def get_customer_contact_persons(context: CliContext[CustomerManagementApplicationContainer], customer_id: str) -> None:
    contact_persons = context.container.customer_query_use_case.get_contact_persons(customer_id)
    context.renderer.as_table(
        data=transform_data(contact_persons), headers=get_headers_from_model(ContactPersonReadModel)
    )

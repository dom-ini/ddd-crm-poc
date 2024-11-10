import click

from building_blocks.presentation.cli.context import CliContext
from building_blocks.presentation.cli.data_processing import transform_data
from building_blocks.presentation.cli.renderer import get_headers_from_model
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.notes.query_model import NoteReadModel
from sales.presentation.container import SalesApplicationContainer


@click.command()
@click.option("--customer-id", type=click.STRING)
@click.option("--salesman-id", type=click.STRING)
@click.option("--contact-phone", type=click.STRING)
@click.option("--contact-email", type=click.STRING)
@click.pass_obj
def get_leads(
    context: CliContext[SalesApplicationContainer],
    customer_id: str,
    salesman_id: str,
    contact_phone: str,
    contact_email: str,
) -> None:
    leads = context.container.lead_query_use_case.get_filtered(
        customer_id=customer_id, owner_id=salesman_id, contact_phone=contact_phone, contact_email=contact_email
    )
    context.renderer.as_table(data=transform_data(leads), headers=get_headers_from_model(LeadReadModel))


@click.command()
@click.argument("lead_id", type=click.STRING)
@click.pass_obj
def get_lead(context: CliContext[SalesApplicationContainer], lead_id: str) -> None:
    lead = context.container.lead_query_use_case.get(lead_id)
    context.renderer.as_table(data=transform_data([lead]), headers=get_headers_from_model(LeadReadModel))


@click.command()
@click.argument("lead_id", type=click.STRING)
@click.pass_obj
def get_lead_assignments(context: CliContext[SalesApplicationContainer], lead_id: str) -> None:
    assignments = context.container.lead_query_use_case.get_assignment_history(lead_id)
    context.renderer.as_table(data=transform_data(assignments), headers=get_headers_from_model(AssignmentReadModel))


@click.command()
@click.argument("lead_id", type=click.STRING)
@click.pass_obj
def get_lead_notes(context: CliContext[SalesApplicationContainer], lead_id: str) -> None:
    notes = context.container.lead_query_use_case.get_notes(lead_id)
    context.renderer.as_table(data=transform_data(notes), headers=get_headers_from_model(NoteReadModel))

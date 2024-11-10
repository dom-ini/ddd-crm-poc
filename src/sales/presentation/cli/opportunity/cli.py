import click

from building_blocks.presentation.cli.context import CliContext
from building_blocks.presentation.cli.data_processing import transform_data
from building_blocks.presentation.cli.renderer import get_headers_from_model
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.query_model import OfferItemReadModel, OpportunityReadModel
from sales.domain.value_objects.opportunity_stage import ALLOWED_OPPORTUNITY_STAGES
from sales.domain.value_objects.priority import ALLOWED_PRIORITY_LEVELS
from sales.presentation.container import SalesApplicationContainer


@click.command()
@click.option("--customer-id", type=click.STRING)
@click.option("--salesman-id", type=click.STRING)
@click.option("--stage", type=click.Choice(ALLOWED_OPPORTUNITY_STAGES))
@click.option("--priority", type=click.Choice(ALLOWED_PRIORITY_LEVELS))
@click.pass_obj
def get_opportunities(
    context: CliContext[SalesApplicationContainer],
    customer_id: str,
    salesman_id: str,
    stage: str,
    priority: str,
) -> None:
    opportunities = context.container.opportunity_query_use_case.get_filtered(
        customer_id=customer_id, owner_id=salesman_id, stage=stage, priority=priority
    )
    context.renderer.as_table(data=transform_data(opportunities), headers=get_headers_from_model(OpportunityReadModel))


@click.command()
@click.argument("opportunity_id", type=click.STRING)
@click.pass_obj
def get_opportunity(context: CliContext[SalesApplicationContainer], opportunity_id: str) -> None:
    opportunity = context.container.opportunity_query_use_case.get(opportunity_id)
    context.renderer.as_table(data=transform_data([opportunity]), headers=get_headers_from_model(OpportunityReadModel))


@click.command()
@click.argument("opportunity_id", type=click.STRING)
@click.pass_obj
def get_opportunity_offer(context: CliContext[SalesApplicationContainer], opportunity_id: str) -> None:
    offer = context.container.opportunity_query_use_case.get_offer(opportunity_id)
    context.renderer.as_table(data=transform_data(offer), headers=get_headers_from_model(OfferItemReadModel))


@click.command()
@click.argument("opportunity_id", type=click.STRING)
@click.pass_obj
def get_opportunity_notes(context: CliContext[SalesApplicationContainer], opportunity_id: str) -> None:
    notes = context.container.opportunity_query_use_case.get_notes(opportunity_id)
    context.renderer.as_table(data=transform_data(notes), headers=get_headers_from_model(NoteReadModel))

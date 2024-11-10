import click

from building_blocks.presentation.cli.context import CliContext
from building_blocks.presentation.cli.data_processing import transform_data
from building_blocks.presentation.cli.renderer import get_headers_from_model
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.presentation.container import SalesApplicationContainer


@click.command()
@click.pass_obj
def get_sales_representatives(
    context: CliContext[SalesApplicationContainer],
) -> None:
    sales_representatives = context.container.sr_query_use_case.get_all()
    context.renderer.as_table(
        data=transform_data(sales_representatives), headers=get_headers_from_model(SalesRepresentativeReadModel)
    )


@click.command()
@click.argument("sales_representative_id", type=click.STRING)
@click.pass_obj
def get_sales_representative(context: CliContext[SalesApplicationContainer], sales_representative_id: str) -> None:
    sales_representative = context.container.sr_query_use_case.get(sales_representative_id)
    context.renderer.as_table(
        data=transform_data([sales_representative]), headers=get_headers_from_model(SalesRepresentativeReadModel)
    )

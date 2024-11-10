import click
from attr import dataclass
from dotenv import load_dotenv

from building_blocks.presentation.cli.renderer import Renderer, RichRenderer
from containers.config import ContainerManager
from containers.container import ApplicationContainer
from customer_management.presentation.cli.customer import cli as customer_cli
from sales.presentation.cli.lead import cli as lead_cli
from sales.presentation.cli.opportunity import cli as opportunity_cli
from sales.presentation.cli.sales_representative import cli as sr_cli


@dataclass
class AppContext:
    renderer: Renderer
    container: ApplicationContainer


def bind_context(click_context: click.Context, app_context: AppContext) -> None:
    click_context.obj = app_context


load_dotenv()


def include_subcommands(app: click.Group) -> None:
    for module in (lead_cli, opportunity_cli, sr_cli, customer_cli):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, click.Command):
                app.add_command(attr)


@click.group()
@click.pass_context
def cli_app(context: click.Context | None = None) -> None:
    app_container = ContainerManager.build()
    renderer = RichRenderer()
    app_context = AppContext(container=app_container, renderer=renderer)
    if context:
        bind_context(context, app_context)


if __name__ == "__main__":
    include_subcommands(cli_app)
    cli_app()

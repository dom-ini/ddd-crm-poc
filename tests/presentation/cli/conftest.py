import pytest
from click.testing import CliRunner

from building_blocks.presentation.cli.renderer import RichRenderer
from containers.container import ApplicationContainer
from entrypoints.cli import AppContext


@pytest.fixture()
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def cli_context(testing_container: ApplicationContainer) -> AppContext:
    renderer = RichRenderer()
    return AppContext(container=testing_container, renderer=renderer)

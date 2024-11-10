import pytest
from click.testing import CliRunner

from entrypoints.cli import AppContext
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.presentation.cli.sales_representative.cli import get_sales_representative, get_sales_representatives
from tests.presentation.cli.utils import calculate_row_count

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("representative_1", "representative_2", "representative_3")
def test_get_sales_representatives_without_filters(cli_runner: CliRunner, cli_context: AppContext) -> None:
    result = cli_runner.invoke(get_sales_representatives, obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 3


def test_get_sales_representative(
    cli_runner: CliRunner, cli_context: AppContext, representative_1: SalesRepresentativeReadModel
) -> None:
    result = cli_runner.invoke(get_sales_representative, [representative_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1

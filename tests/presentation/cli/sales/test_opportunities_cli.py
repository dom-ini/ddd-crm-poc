import pytest
from click.testing import CliRunner

from entrypoints.cli import AppContext
from sales.application.opportunity.query_model import OpportunityReadModel
from sales.presentation.cli.opportunity.cli import (
    get_opportunities,
    get_opportunity,
    get_opportunity_notes,
    get_opportunity_offer,
)
from tests.presentation.cli.utils import calculate_row_count

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("opportunity_1", "opportunity_2", "opportunity_3")
def test_get_opportunities_without_filters(cli_runner: CliRunner, cli_context: AppContext) -> None:
    result = cli_runner.invoke(get_opportunities, obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 3


@pytest.mark.usefixtures("opportunity_1", "opportunity_2", "opportunity_3")
def test_get_opportunities_with_filters(
    cli_runner: CliRunner, cli_context: AppContext, opportunity_2: OpportunityReadModel
) -> None:
    result = cli_runner.invoke(
        get_opportunities,
        [
            "--customer-id",
            opportunity_2.customer_id,
            "--salesman-id",
            opportunity_2.owner_id,
            "--stage",
            opportunity_2.stage,
            "--priority",
            opportunity_2.priority,
        ],
        obj=cli_context,
    )

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_opportunity(cli_runner: CliRunner, cli_context: AppContext, opportunity_1: OpportunityReadModel) -> None:
    result = cli_runner.invoke(get_opportunity, [opportunity_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_opportunity_offer(
    cli_runner: CliRunner, cli_context: AppContext, opportunity_1: OpportunityReadModel
) -> None:
    result = cli_runner.invoke(get_opportunity_offer, [opportunity_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_opportunity_notes(
    cli_runner: CliRunner, cli_context: AppContext, opportunity_1: OpportunityReadModel
) -> None:
    result = cli_runner.invoke(get_opportunity_notes, [opportunity_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1

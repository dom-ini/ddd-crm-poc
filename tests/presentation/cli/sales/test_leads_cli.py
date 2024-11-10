import pytest
from click.testing import CliRunner

from entrypoints.cli import AppContext
from sales.application.lead.query_model import LeadReadModel
from sales.presentation.cli.lead.cli import get_lead, get_lead_assignments, get_lead_notes, get_leads
from tests.presentation.cli.utils import calculate_row_count

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("lead_1", "lead_2")
def test_get_leads_without_filters(cli_runner: CliRunner, cli_context: AppContext) -> None:
    result = cli_runner.invoke(get_leads, obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 2


@pytest.mark.usefixtures("lead_1", "lead_2")
def test_get_leads_with_filters(cli_runner: CliRunner, cli_context: AppContext, lead_2: LeadReadModel) -> None:
    result = cli_runner.invoke(
        get_leads,
        [
            "--customer-id",
            lead_2.customer_id,
            "--salesman-id",
            lead_2.assigned_salesman_id,
            "--contact-phone",
            lead_2.contact_data.phone,
            "--contact-email",
            lead_2.contact_data.email,
        ],
        obj=cli_context,
    )

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_lead(cli_runner: CliRunner, cli_context: AppContext, lead_1: LeadReadModel) -> None:
    result = cli_runner.invoke(get_lead, [lead_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_lead_assignments(cli_runner: CliRunner, cli_context: AppContext, lead_1: LeadReadModel) -> None:
    result = cli_runner.invoke(get_lead_assignments, [lead_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_lead_notes(cli_runner: CliRunner, cli_context: AppContext, lead_1: LeadReadModel) -> None:
    result = cli_runner.invoke(get_lead_notes, [lead_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1

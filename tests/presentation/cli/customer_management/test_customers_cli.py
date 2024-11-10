import pytest
from click.testing import CliRunner

from customer_management.application.query_model import CustomerReadModel
from customer_management.presentation.cli.customer.cli import get_customer, get_customer_contact_persons, get_customers
from entrypoints.cli import AppContext
from tests.presentation.cli.utils import calculate_row_count

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("customer_1", "customer_2", "customer_3", "customer_4")
def test_get_customers_without_filters(cli_runner: CliRunner, cli_context: AppContext) -> None:
    result = cli_runner.invoke(get_customers, obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 4


@pytest.mark.usefixtures("customer_1", "customer_2", "customer_3", "customer_4")
def test_get_customers_with_filters(
    cli_runner: CliRunner, cli_context: AppContext, customer_2: CustomerReadModel
) -> None:
    result = cli_runner.invoke(
        get_customers,
        [
            "--relation-manager-id",
            customer_2.relation_manager_id,
            "--status",
            customer_2.status,
            "--company-name",
            customer_2.company_info.name,
            "--industry",
            customer_2.company_info.industry,
            "--company-size",
            customer_2.company_info.size,
            "--legal-form",
            customer_2.company_info.legal_form,
        ],
        obj=cli_context,
    )

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_customer(cli_runner: CliRunner, cli_context: AppContext, customer_1: CustomerReadModel) -> None:
    result = cli_runner.invoke(get_customer, [customer_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1


def test_get_customer_contact_persons(
    cli_runner: CliRunner, cli_context: AppContext, customer_1: CustomerReadModel
) -> None:
    result = cli_runner.invoke(get_customer_contact_persons, [customer_1.id], obj=cli_context)

    results_count = calculate_row_count(result.output)
    assert result.exit_code == 0
    assert not result.exception
    assert results_count == 1

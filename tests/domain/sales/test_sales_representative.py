import pytest

from sales.domain.entities.sales_representative import SalesRepresentative


@pytest.fixture()
def sales_representative() -> SalesRepresentative:
    return SalesRepresentative(id="sr_1", first_name="Jan", last_name="Kowalski")


def test_sales_representative_creation(
    sales_representative: SalesRepresentative,
) -> None:
    assert sales_representative.id == "sr_1"
    assert sales_representative.first_name == "Jan"
    assert sales_representative.last_name == "Kowalski"


def test_sales_representative_reconstitution() -> None:
    sales_representative = SalesRepresentative.reconstitute(id="sr_1", first_name="Jan", last_name="Kowalski")

    assert sales_representative.id == "sr_1"
    assert sales_representative.first_name == "Jan"
    assert sales_representative.last_name == "Kowalski"

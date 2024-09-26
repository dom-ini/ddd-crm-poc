import pytest

from sales.domain.entities.sales_representative import SalesRepresentative
from sales.domain.exceptions import SalesRepresentativeCanOnlyModifyItsOwnData


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


def test_sales_representative_update(sales_representative: SalesRepresentative) -> None:
    new_first_name = "Marcin"
    new_last_name = "Iksiński"

    sales_representative.update(
        editor_id=sales_representative.id,
        first_name=new_first_name,
        last_name=new_last_name,
    )

    assert sales_representative.first_name == new_first_name
    assert sales_representative.last_name == new_last_name


def test_sales_representative_partial_update(
    sales_representative: SalesRepresentative,
) -> None:
    new_first_name = "Marcin"
    old_last_name = sales_representative.last_name

    sales_representative.update(
        editor_id=sales_representative.id,
        first_name=new_first_name,
    )

    assert sales_representative.first_name == new_first_name
    assert sales_representative.last_name == old_last_name


def test_sales_representative_update_by_non_owner_should_fail(
    sales_representative: SalesRepresentative,
) -> None:
    with pytest.raises(SalesRepresentativeCanOnlyModifyItsOwnData):
        sales_representative.update(editor_id="non owner id", first_name="Jan")

from collections.abc import Sequence

import pytest

from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.infrastructure.file.sales_representative.query_service import SalesRepresentativeFileQueryService
from tests.infrastructure.file.conftest import SALES_REPRESENTATIVE_TEST_DATA_PATH

pytestmark = pytest.mark.integration


@pytest.fixture()
def all_srs(
    representative_1: SalesRepresentativeReadModel,
    representative_2: SalesRepresentativeReadModel,
    representative_3: SalesRepresentativeReadModel,
) -> Sequence[SalesRepresentativeReadModel]:
    return (representative_1, representative_2, representative_3)


@pytest.fixture()
def query_service() -> SalesRepresentativeFileQueryService:
    return SalesRepresentativeFileQueryService(sr_file_path=SALES_REPRESENTATIVE_TEST_DATA_PATH)


def test_get_sr(
    query_service: SalesRepresentativeFileQueryService,
    representative_1: SalesRepresentativeReadModel,
) -> None:
    representative = query_service.get(representative_id=representative_1.id)

    assert representative is not None
    assert representative.id == representative_1.id


def test_get_all(
    query_service: SalesRepresentativeFileQueryService,
    all_srs: Sequence[SalesRepresentativeReadModel],
) -> None:
    representatives = query_service.get_all()

    fetched_representatives_ids = set(sr.id for sr in representatives)
    representatives_ids = set(sr.id for sr in all_srs)
    assert fetched_representatives_ids == representatives_ids


def test_get_should_return_none_if_not_found(
    query_service: SalesRepresentativeFileQueryService,
) -> None:
    representative = query_service.get(representative_id="invalid id")

    assert representative is None

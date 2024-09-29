from collections.abc import Iterator, Sequence

import pytest

from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.application.sales_representative.command_model import SalesRepresentativeCreateModel
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.infrastructure.file.sales_representative.command import SalesRepresentativeFileUnitOfWork
from sales.infrastructure.file.sales_representative.query_service import SalesRepresentativeFileQueryService
from tests.infrastructure.file.conftest import TEST_DATA_FOLDER

pytestmark = pytest.mark.integration

SR_QUERY_DB_FILE = "test-query-representatives"
TEST_DATA_PATH = TEST_DATA_FOLDER / SR_QUERY_DB_FILE


@pytest.fixture(scope="session")
def command_use_case() -> SalesRepresentativeCommandUseCase:
    uow = SalesRepresentativeFileUnitOfWork(file_path=TEST_DATA_PATH)
    command_use_case = SalesRepresentativeCommandUseCase(sr_uow=uow)
    return command_use_case


@pytest.fixture(scope="session", autouse=True)
def sr_1(
    command_use_case: SalesRepresentativeCommandUseCase,
) -> SalesRepresentativeReadModel:
    data = SalesRepresentativeCreateModel(first_name="Jan", last_name="Kowalski")
    sr = command_use_case.create(data=data)
    return sr


@pytest.fixture(scope="session", autouse=True)
def sr_2(
    command_use_case: SalesRepresentativeCommandUseCase,
) -> SalesRepresentativeReadModel:
    data = SalesRepresentativeCreateModel(first_name="Piotr", last_name="Nowak")
    sr = command_use_case.create(data=data)
    return sr


@pytest.fixture(scope="session", autouse=True)
def sr_3(
    command_use_case: SalesRepresentativeCommandUseCase,
) -> SalesRepresentativeReadModel:
    data = SalesRepresentativeCreateModel(first_name="Paweł", last_name="Kowalczyk")
    sr = command_use_case.create(data=data)
    return sr


@pytest.fixture()
def all_srs(
    sr_1: SalesRepresentativeReadModel,
    sr_2: SalesRepresentativeReadModel,
    sr_3: SalesRepresentativeReadModel,
) -> Sequence[SalesRepresentativeReadModel]:
    return (sr_1, sr_2, sr_3)


@pytest.fixture(scope="session", autouse=True)
def clean_data() -> Iterator[None]:
    yield
    for file in TEST_DATA_FOLDER.iterdir():
        if file.name.startswith(SR_QUERY_DB_FILE):
            file.unlink()


@pytest.fixture()
def query_service() -> SalesRepresentativeFileQueryService:
    return SalesRepresentativeFileQueryService(sr_file_path=TEST_DATA_PATH)


def test_get_sr(
    query_service: SalesRepresentativeFileQueryService,
    sr_1: SalesRepresentativeReadModel,
) -> None:
    representative = query_service.get(representative_id=sr_1.id)

    assert representative is not None
    assert representative.id == sr_1.id


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

from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import ObjectDoesNotExist, UnauthorizedAction
from sales.application.sales_representative.command import (
    SalesRepresentativeCommandUseCase,
    SalesRepresentativeUnitOfWork,
)
from sales.domain.entities.sales_representative import SalesRepresentative
from sales.domain.exceptions import SalesRepresentativeCanOnlyModifyItsOwnData
from sales.domain.repositories.sales_representative import SalesRepresentativeRepository


@pytest.fixture()
def mock_sr_repository() -> SalesRepresentativeRepository:
    repository = MagicMock(spec=SalesRepresentativeRepository)
    return repository


@pytest.fixture()
def sr_uow(
    mock_sr_repository: SalesRepresentativeRepository,
) -> SalesRepresentativeUnitOfWork:
    uow = MagicMock(spec=SalesRepresentativeUnitOfWork)
    uow.repository = mock_sr_repository
    return uow


@pytest.fixture()
def sr_command_use_case(
    sr_uow: SalesRepresentativeUnitOfWork,
) -> SalesRepresentativeCommandUseCase:
    return SalesRepresentativeCommandUseCase(sr_uow=sr_uow)


@pytest.fixture()
def mock_sales_representative() -> MagicMock:
    return MagicMock(spec=SalesRepresentative)


def test_update_with_wrong_id_should_fail(
    sr_uow: SalesRepresentativeUnitOfWork,
    sr_command_use_case: SalesRepresentativeCommandUseCase,
) -> None:
    sr_id = "invalid id"
    sr_uow.__enter__().repository.get.return_value = None

    with pytest.raises(ObjectDoesNotExist):
        sr_command_use_case.update(representative_id=sr_id, editor_id="irrelevant", data=MagicMock())


def test_update_by_unauthorized_user_should_fail(
    sr_uow: SalesRepresentativeUnitOfWork,
    sr_command_use_case: SalesRepresentativeCommandUseCase,
    mock_sales_representative: MagicMock,
) -> None:
    sr_uow.__enter__().repository.get.return_value = mock_sales_representative
    mock_sales_representative.update.side_effect = SalesRepresentativeCanOnlyModifyItsOwnData

    with pytest.raises(UnauthorizedAction):
        sr_command_use_case.update(representative_id="sr-1", editor_id="sr-2", data=MagicMock())

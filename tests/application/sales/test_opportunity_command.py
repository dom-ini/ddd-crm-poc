from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import ForbiddenAction, InvalidData, ObjectDoesNotExist
from building_blocks.domain.exceptions import DomainException
from sales.application.opportunity.command import OpportunityCommandUseCase, OpportunityUnitOfWork
from sales.application.opportunity.command_model import (
    CurrencyCreateUpdateModel,
    MoneyCreateUpdateModel,
    OfferItemCreateUpdateModel,
    OpportunityCreateModel,
    OpportunityUpdateModel,
    ProductCreateUpdateModel,
)
from sales.domain.entities.opportunity import Opportunity
from sales.domain.exceptions import OnlyOwnerCanEditNotes, OnlyOwnerCanModifyOffer, OnlyOwnerCanModifyOpportunityData
from sales.domain.repositories.opportunity import OpportunityRepository
from sales.domain.service.shared import SalesCustomerStatusName

valid_offer_item_example = OfferItemCreateUpdateModel(
    product=ProductCreateUpdateModel(name="product"),
    value=MoneyCreateUpdateModel(
        currency=CurrencyCreateUpdateModel(name="US dollar", iso_code="USD"),
        amount=Decimal("100"),
    ),
)
invalid_offer_item_example = OfferItemCreateUpdateModel(
    product=ProductCreateUpdateModel(name="product"),
    value=MoneyCreateUpdateModel(
        currency=CurrencyCreateUpdateModel(name="US dollar", iso_code="USD"),
        amount=Decimal("0"),
    ),
)


@pytest.fixture()
def mock_opportunity_repository() -> OpportunityRepository:
    repository = MagicMock(spec=OpportunityRepository)
    return repository


@pytest.fixture()
def opportunity_uow(
    mock_opportunity_repository: OpportunityRepository,
) -> OpportunityUnitOfWork:
    uow = MagicMock(spec=OpportunityUnitOfWork)
    uow.repository = mock_opportunity_repository
    return uow


@pytest.fixture()
def opportunity_command_use_case(
    opportunity_uow: OpportunityUnitOfWork,
) -> OpportunityCommandUseCase:
    customer_service = MagicMock()
    salesman_uow = MagicMock()
    return OpportunityCommandUseCase(
        opportunity_uow=opportunity_uow,
        salesman_uow=salesman_uow,
        customer_service=customer_service,
    )


@pytest.fixture()
def mock_opportunity() -> MagicMock:
    return MagicMock(spec=Opportunity)


@pytest.mark.parametrize(
    "data",
    [
        OpportunityCreateModel(
            customer_id="customer_1",
            source="invalid source",
            priority="medium",
            offer=[valid_offer_item_example],
        ),
        OpportunityCreateModel(
            customer_id="customer_1",
            source="website",
            priority="invalid priority",
            offer=[valid_offer_item_example],
        ),
        OpportunityCreateModel(
            customer_id="customer_1",
            source="website",
            priority="medium",
            offer=[invalid_offer_item_example],
        ),
    ],
)
def test_create_opportunity_correctly_raises_invalid_data(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
    data: OpportunityCreateModel,
) -> None:
    with pytest.raises(InvalidData):
        opportunity_command_use_case.create(creator_id="salesman-1", data=data)

    opportunity_uow.__enter__().repository.create.assert_not_called()


def test_create_opportunity_with_invalid_customer_id_should_fail(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
) -> None:
    opportunity_command_use_case.customer_service.customer_exists.return_value = False
    data = MagicMock()

    with pytest.raises(InvalidData):
        opportunity_command_use_case.create(data=data, creator_id="salesman-1")

    opportunity_uow.__enter__().repository.create.assert_not_called()


def test_create_opportunity_with_invalid_salesman_id_should_fail(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
) -> None:
    opportunity_command_use_case.salesman_uow.__enter__().repository.get.return_value = None
    data = MagicMock()

    with pytest.raises(InvalidData):
        opportunity_command_use_case.create(data=data, creator_id="invalid id")

    opportunity_uow.__enter__().repository.create.assert_not_called()


def test_create_opportunity_should_fail_if_customer_has_not_converted_status(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
) -> None:
    opportunity_uow.__enter__().repository.get_for_customer.return_value = None
    opportunity_command_use_case.customer_service.get_customer_status.return_value = SalesCustomerStatusName.INITIAL
    data = OpportunityCreateModel(
        customer_id="customer_1",
        source="ads",
        priority="medium",
        offer=[valid_offer_item_example],
    )

    with pytest.raises(InvalidData):
        opportunity_command_use_case.create(data=data, creator_id="salesman-1")

    opportunity_uow.__enter__().repository.create.assert_not_called()


@pytest.mark.parametrize(
    "data",
    [
        OpportunityUpdateModel(
            source="invalid source",
            priority="medium",
            stage="closed-won",
        ),
        OpportunityUpdateModel(
            source="website",
            priority="invalid priority",
            stage="closed-won",
        ),
        OpportunityUpdateModel(
            source="website",
            priority="medium",
            stage="invalid stage",
        ),
    ],
)
def test_update_opportunity_correctly_raises_invalid_data(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
    data: OpportunityUpdateModel,
) -> None:
    with pytest.raises(InvalidData):
        opportunity_command_use_case.update(opportunity_id="opp-1", editor_id="salesman-1", data=data)

    opportunity_uow.__enter__().repository.update.assert_not_called()


def test_update_offer_correctly_raises_invalid_data(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
) -> None:
    with pytest.raises(InvalidData):
        opportunity_command_use_case.update_offer(
            opportunity_id="opp-1",
            editor_id="salesman-1",
            data=[invalid_offer_item_example],
        )

    opportunity_uow.__enter__().repository.update.assert_not_called()


@pytest.mark.parametrize(
    "method_name,data_field_name",
    [
        ("update", "lead_data"),
        ("update_note", "note_data"),
        ("update_assignment", "assignment_data"),
    ],
)
def calling_method_with_wrong_opportunity_id_should_fail(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
    method_name: str,
    data_field_name: str,
) -> None:
    opportunity_id = "invalid id"
    data = MagicMock()
    opportunity_uow.__enter__().repository.get.return_value = None
    kwargs = {
        "opportunity_id": opportunity_id,
        data_field_name: data,
        "editor_id": "salesman-1",
    }

    with pytest.raises(ObjectDoesNotExist):
        getattr(opportunity_command_use_case, method_name)(**kwargs)

    opportunity_uow.__enter__().repository.update.assert_not_called()


@pytest.mark.parametrize(
    "method_name,domain_method_name,exception_class,data_kwargs",
    [
        (
            "update",
            "update",
            OnlyOwnerCanModifyOpportunityData,
            {
                "data": OpportunityUpdateModel(source="website", priority="medium", stage="proposal"),
            },
        ),
        (
            "update_offer",
            "modify_offer",
            OnlyOwnerCanModifyOffer,
            {"data": [valid_offer_item_example]},
        ),
        (
            "update_note",
            "change_note",
            OnlyOwnerCanEditNotes,
            {"note_data": MagicMock()},
        ),
    ],
)
def test_calling_method_by_unauthorized_user_should_fail(
    opportunity_uow: OpportunityUnitOfWork,
    opportunity_command_use_case: OpportunityCommandUseCase,
    mock_opportunity: MagicMock,
    method_name: str,
    domain_method_name: str,
    exception_class: type[DomainException],
    data_kwargs: dict,
) -> None:
    opportunity_uow.__enter__().repository.get.return_value = mock_opportunity
    getattr(mock_opportunity, domain_method_name).side_effect = exception_class

    with pytest.raises(ForbiddenAction):
        getattr(opportunity_command_use_case, method_name)(
            opportunity_id="opp-1", editor_id="salesman-1", **data_kwargs
        )

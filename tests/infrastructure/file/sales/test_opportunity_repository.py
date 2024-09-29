from uuid import uuid4

import pytest
from attrs import define

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.infrastructure.file.opportunity.repository import OpportunityFileRepository

pytestmark = pytest.mark.integration


@define
class DummyOpportunity:
    id: str
    owner_id: str


@pytest.fixture(scope="session")
def opportunity() -> DummyOpportunity:
    return DummyOpportunity(id=str(uuid4()), owner_id="some id")


@pytest.fixture(scope="session")
def opportunity_repo() -> OpportunityFileRepository:
    return OpportunityFileRepository(db={})


@pytest.fixture()
def create_opportunity(opportunity_repo: OpportunityFileRepository, opportunity: DummyOpportunity) -> None:
    opportunity_repo.create(opportunity)


@pytest.mark.usefixtures("create_opportunity")
def test_create_and_get(opportunity_repo: OpportunityFileRepository, opportunity: DummyOpportunity) -> None:
    fetched_opportunity = opportunity_repo.get(opportunity.id)

    assert fetched_opportunity is not None
    assert fetched_opportunity.id == opportunity.id


def test_get_should_return_none_if_not_found(
    opportunity_repo: OpportunityFileRepository,
) -> None:
    fetched_opportunity = opportunity_repo.get("invalid id")

    assert fetched_opportunity is None


def test_create_with_existing_id_should_fail(
    opportunity_repo: OpportunityFileRepository, opportunity: DummyOpportunity
) -> None:
    with pytest.raises(ObjectAlreadyExists):
        opportunity_repo.create(opportunity)


def test_update(opportunity_repo: OpportunityFileRepository, opportunity: DummyOpportunity) -> None:
    new_salesman_id = "new id"
    updated_opportunity = DummyOpportunity(id=opportunity.id, owner_id=new_salesman_id)

    opportunity_repo.update(updated_opportunity)

    fetched_opportunity = opportunity_repo.get(opportunity.id)
    assert fetched_opportunity.owner_id == new_salesman_id

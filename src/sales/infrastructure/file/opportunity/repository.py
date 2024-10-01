import shelve
from collections.abc import Sequence

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.domain.entities.opportunity import Opportunity
from sales.domain.repositories.opportunity import OpportunityRepository


class OpportunityFileRepository(OpportunityRepository):
    def __init__(self, db: shelve.Shelf) -> None:
        self.db = db

    def get(self, opportunity_id: str) -> Opportunity | None:
        opportunity = self.db.get(opportunity_id)
        return opportunity

    def get_all_by_customer(self, customer_id: str) -> Sequence[Opportunity]:
        opportunities = tuple(opportunity for opportunity in self.db.values() if opportunity.customer_id == customer_id)
        return opportunities

    def create(self, opportunity: Opportunity) -> None:
        if opportunity.id in self.db:
            raise ObjectAlreadyExists(f"Opportunity with id={opportunity.id} already exists")
        self.db[opportunity.id] = opportunity

    def update(self, opportunity: Opportunity) -> None:
        self.db[opportunity.id] = opportunity

import shelve

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.domain.entities.lead import Lead
from sales.domain.repositories.lead import LeadRepository


class LeadFileRepository(LeadRepository):
    def __init__(self, db: shelve.Shelf) -> None:
        self.db = db

    def get(self, lead_id: str) -> Lead | None:
        lead = self.db.get(lead_id)
        return lead

    def create(self, lead: Lead) -> None:
        if lead.id in self.db:
            raise ObjectAlreadyExists(f"Lead with id={lead.id} already exists")
        self.db[lead.id] = lead

    def update(self, lead: Lead) -> None:
        self.db[lead.id] = lead

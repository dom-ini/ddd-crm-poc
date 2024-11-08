from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from building_blocks.infrastructure.file.command import FileLikeDB
from sales.domain.entities.lead import Lead
from sales.domain.repositories.lead import LeadRepository


class LeadFileRepository(LeadRepository):
    def __init__(self, db: FileLikeDB) -> None:
        self.db = db

    def get(self, lead_id: str) -> Lead | None:
        lead = self.db.get(lead_id)
        return lead

    def get_by_customer(self, customer_id: str) -> Lead | None:
        for lead in self.db.values():
            if lead.customer_id == customer_id:
                return lead
        return None

    def create(self, lead: Lead) -> None:
        if lead.id in self.db:
            raise ObjectAlreadyExists(f"Lead with id={lead.id} already exists")
        self.db[lead.id] = lead

    def update(self, lead: Lead) -> None:
        self.db[lead.id] = lead

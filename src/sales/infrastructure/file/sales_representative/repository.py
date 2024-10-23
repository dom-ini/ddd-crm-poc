from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from building_blocks.infrastructure.file.command import FileLikeDB
from sales.domain.entities.sales_representative import SalesRepresentative
from sales.domain.repositories.sales_representative import SalesRepresentativeRepository


class SalesRepresentativeFileRepository(SalesRepresentativeRepository):
    def __init__(self, db: FileLikeDB) -> None:
        self.db = db

    def get(self, representative_id: str) -> SalesRepresentative | None:
        representative = self.db.get(representative_id)
        return representative

    def create(self, representative: SalesRepresentative) -> None:
        if representative.id in self.db:
            raise ObjectAlreadyExists(f"Sales representative with id={representative.id} already exists")
        self.db[representative.id] = representative

    def update(self, representative: SalesRepresentative) -> None:
        self.db[representative.id] = representative

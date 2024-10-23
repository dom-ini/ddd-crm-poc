from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.domain.entities.sales_representative import SalesRepresentative
from sales.domain.repositories.sales_representative import SalesRepresentativeRepository
from sales.infrastructure.sql.sales_representative.models import SalesRepresentativeModel


class SalesRepresentativeSQLRepository(SalesRepresentativeRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, representative_id: str) -> SalesRepresentative | None:
        query = select(SalesRepresentativeModel).where(SalesRepresentativeModel.id == representative_id)
        representative = self.db.scalar(query)
        if not representative:
            return None
        return representative.to_domain()

    def create(self, representative: SalesRepresentative) -> None:
        representative_in_db = SalesRepresentativeModel.from_domain(representative)
        try:
            self.db.add(representative_in_db)
        except IntegrityError as e:
            raise ObjectAlreadyExists(f"Sales representative with id={representative.id} already exists") from e

    def update(self, representative: SalesRepresentative) -> None:
        updated_representative = SalesRepresentativeModel.from_domain(representative)
        self.db.merge(updated_representative)

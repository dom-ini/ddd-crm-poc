from collections.abc import Sequence

from sqlalchemy import select

from building_blocks.infrastructure.sql.db import SessionFactory
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.application.sales_representative.query_service import SalesRepresentativeQueryService
from sales.domain.entities.sales_representative import SalesRepresentative
from sales.infrastructure.sql.sales_representative.models import SalesRepresentativeModel


class SalesRepresentativeSQLQueryService(SalesRepresentativeQueryService):
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def _get_single_representative(self, representative_id: str) -> SalesRepresentative | None:
        query = select(SalesRepresentativeModel).where(SalesRepresentativeModel.id == representative_id)
        with self._session_factory() as db:
            representative = db.scalar(query)
            if representative is None:
                return None
            return representative.to_domain()

    def get(self, representative_id: str) -> SalesRepresentativeReadModel | None:
        representative = self._get_single_representative(representative_id)
        if representative is None:
            return None
        return SalesRepresentativeReadModel.from_domain(representative)

    def get_all(self) -> Sequence[SalesRepresentativeReadModel]:
        query = select(SalesRepresentativeModel)
        with self._session_factory() as db:
            representatives = tuple(representative.to_domain() for representative in db.scalars(query))
        return tuple(SalesRepresentativeReadModel.from_domain(representative) for representative in representatives)

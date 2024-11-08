from collections.abc import Iterable

from building_blocks.application.exceptions import ObjectDoesNotExist
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.application.sales_representative.query_service import SalesRepresentativeQueryService


class SalesRepresentativeQueryUseCase:
    def __init__(self, sr_query_service: SalesRepresentativeQueryService) -> None:
        self.sr_query_service = sr_query_service

    def get(self, representative_id: str) -> SalesRepresentativeReadModel:
        representative = self.sr_query_service.get(representative_id)
        if representative is None:
            raise ObjectDoesNotExist(representative_id)
        return representative

    def get_all(self) -> Iterable[SalesRepresentativeReadModel]:
        representatives = self.sr_query_service.get_all()
        return representatives

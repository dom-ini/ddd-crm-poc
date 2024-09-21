from collections.abc import Iterable

from building_blocks.infrastructure.file.io import get_read_db
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.application.sales_representative.query_service import SalesRepresentativeQueryService
from sales.domain.entities.sales_representative import SalesRepresentative
from sales.infrastructure.file import config


class SalesRepresentativeFileQueryService(SalesRepresentativeQueryService):
    def __init__(
        self,
        sr_file_path: str = config.SALES_REPR_FILE_PATH,
    ) -> None:
        self._file_path = sr_file_path

    def _get_single_representative(self, representative_id: str) -> SalesRepresentative | None:
        with get_read_db(self._file_path) as db:
            representative = db.get(representative_id)
        return representative

    def get(self, representative_id: str) -> SalesRepresentativeReadModel | None:
        representative = self._get_single_representative(representative_id)
        if representative is None:
            return None
        return SalesRepresentativeReadModel.from_domain(representative)

    def get_all(self) -> Iterable[SalesRepresentativeReadModel]:
        with get_read_db(self._file_path) as db:
            all_ids = db.keys()
            representatives = [SalesRepresentativeReadModel.from_domain(db.get(id)) for id in all_ids]
        return tuple(representatives)

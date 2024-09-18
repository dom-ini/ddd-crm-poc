from uuid import uuid4
from building_blocks.application.command import BaseUnitOfWork
from sales.domain.repositories.sales_representative import SalesRepresentativeRepository
from sales.application.sales_representative.query_model import (
    SalesRepresentativeReadModel,
)
from sales.application.sales_representative.command_model import (
    SalesRepresentativeCreateModel,
    SalesRepresentativeUpdateModel,
)
from sales.domain.entities.sales_representative import SalesRepresentative
from building_blocks.application.exceptions import ObjectDoesNotExist


class SalesRepresentativeUnitOfWork(BaseUnitOfWork):
    repository: SalesRepresentativeRepository


class SalesRepresentativeCommandUseCase:
    def __init__(self, sr_uow: SalesRepresentativeUnitOfWork) -> None:
        self.sr_uow = sr_uow

    def create(
        self, data: SalesRepresentativeCreateModel
    ) -> SalesRepresentativeReadModel:
        representative_id = str(uuid4())
        representative = SalesRepresentative(
            id=representative_id, first_name=data.first_name, last_name=data.last_name
        )
        with self.sr_uow as uow:
            uow.repository.create(representative)
        return SalesRepresentativeReadModel.from_domain(representative)

    def update(
        self, representative_id: str, data: SalesRepresentativeUpdateModel
    ) -> SalesRepresentativeReadModel:
        with self.sr_uow as uow:
            representative = self._get_representative(
                uow=uow, representative_id=representative_id
            )
            if data.first_name is not None:
                representative.first_name = data.first_name
            if data.last_name is not None:
                representative.last_name = data.last_name
            uow.repository.update(representative)
        return SalesRepresentativeReadModel.from_domain(representative)

    def _get_representative(
        self, uow: SalesRepresentativeUnitOfWork, representative_id: str
    ) -> SalesRepresentative:
        representative = uow.repository.get(representative_id)
        if representative is None:
            raise ObjectDoesNotExist(representative_id)
        return representative
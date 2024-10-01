from collections.abc import Iterable
from typing import TypeVar
from uuid import uuid4

from building_blocks.application.command import BaseUnitOfWork
from building_blocks.application.exceptions import InvalidData, ObjectDoesNotExist, UnauthorizedAction
from building_blocks.domain.exceptions import ValueNotAllowed
from building_blocks.domain.value_object import ValueObject
from sales.application.acl import ICustomerService
from sales.application.notes.command_model import NoteCreateModel
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.command_model import (
    OfferItemCreateUpdateModel,
    OpportunityCreateModel,
    OpportunityUpdateModel,
)
from sales.application.opportunity.query_model import OfferItemReadModel, OpportunityReadModel
from sales.application.sales_representative.command import SalesRepresentativeUnitOfWork
from sales.application.service import CustomerServiceMixin, SalesRepresentativeServiceMixin
from sales.domain.entities.opportunity import Opportunity
from sales.domain.exceptions import (
    AmountMustBeGreaterThanZero,
    OnlyOwnerCanEditNotes,
    OnlyOwnerCanModifyOffer,
    OnlyOwnerCanModifyOpportunityData,
)
from sales.domain.repositories.opportunity import OpportunityRepository
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.money.money import Money
from sales.domain.value_objects.offer_item import OfferItem
from sales.domain.value_objects.opportunity_stage import INITIAL_STAGE, OpportunityStage
from sales.domain.value_objects.priority import Priority
from sales.domain.value_objects.product import Product

ValueObjectT = TypeVar("ValueObjectT", bound=ValueObject)


class OpportunityUnitOfWork(BaseUnitOfWork):
    repository: OpportunityRepository


class OpportunityCommandUseCase(CustomerServiceMixin, SalesRepresentativeServiceMixin):
    def __init__(
        self,
        opportunity_uow: OpportunityUnitOfWork,
        salesman_uow: SalesRepresentativeUnitOfWork,
        customer_service: ICustomerService,
    ) -> None:
        self.opportunity_uow = opportunity_uow
        self.salesman_uow = salesman_uow
        self.customer_service = customer_service

    def create(self, data: OpportunityCreateModel, creator_id: str) -> OpportunityReadModel:
        self._verify_that_salesman_exists(creator_id)
        self._verify_that_customer_exists(data.customer_id)

        opportunity_id = str(uuid4())
        source = self._create_source(data.source)
        stage = self._create_stage()
        priority = self._create_priority(data.priority)
        offer = self._create_offer(data.offer)
        opportunity = Opportunity.make(
            id=opportunity_id,
            created_by_id=creator_id,
            customer_id=data.customer_id,
            source=source,
            stage=stage,
            priority=priority,
            offer=offer,
        )
        with self.opportunity_uow as uow:
            uow.repository.create(opportunity)
        return OpportunityReadModel.from_domain(opportunity)

    def update(self, opportunity_id: str, editor_id: str, data: OpportunityUpdateModel) -> OpportunityReadModel:
        with self.opportunity_uow as uow:
            opportunity = self._get_opportunity(uow=uow, opportunity_id=opportunity_id)
            try:
                opportunity.update(
                    editor_id=editor_id,
                    source=self._create_source_if_provided(data.source),
                    stage=self._create_stage_if_provided(data.stage),
                    priority=self._create_priority_if_provided(data.priority),
                )
            except OnlyOwnerCanModifyOpportunityData as e:
                raise UnauthorizedAction(e.message) from e
            uow.repository.update(opportunity)
        return OpportunityReadModel.from_domain(opportunity)

    def update_offer(
        self,
        opportunity_id: str,
        editor_id: str,
        data: Iterable[OfferItemCreateUpdateModel],
    ) -> Iterable[OfferItemCreateUpdateModel]:
        with self.opportunity_uow as uow:
            opportunity = self._get_opportunity(uow=uow, opportunity_id=opportunity_id)
            new_offer = self._create_offer(data)
            try:
                opportunity.modify_offer(new_offer=new_offer, editor_id=editor_id)
            except OnlyOwnerCanModifyOffer as e:
                raise UnauthorizedAction(e.message) from e
            uow.repository.update(opportunity)
        return tuple(OfferItemReadModel.from_domain(item) for item in new_offer)

    def update_note(self, opportunity_id: str, editor_id: str, note_data: NoteCreateModel) -> NoteReadModel:
        with self.opportunity_uow as uow:
            opportunity = self._get_opportunity(uow=uow, opportunity_id=opportunity_id)
            try:
                opportunity.change_note(new_content=note_data.content, editor_id=editor_id)
            except OnlyOwnerCanEditNotes as e:
                raise UnauthorizedAction(e.message) from e
            uow.repository.update(opportunity)
        return NoteReadModel.from_domain(opportunity.note)

    def _get_opportunity(self, uow: OpportunityUnitOfWork, opportunity_id: str) -> Opportunity:
        opportunity = uow.repository.get(opportunity_id)
        if opportunity is None:
            raise ObjectDoesNotExist(opportunity_id)
        return opportunity

    def _create_source_if_provided(self, source_name: str | None) -> AcquisitionSource | None:
        return self._create_source(source_name) if source_name else None

    def _create_stage_if_provided(self, stage_name: str | None) -> OpportunityStage | None:
        return self._create_stage(stage_name) if stage_name else None

    def _create_priority_if_provided(self, priority_level: str | None) -> Priority | None:
        return self._create_priority(priority_level) if priority_level else None

    def _create_source(self, source_name: str) -> AcquisitionSource:
        return self._create_constrained_value_object(AcquisitionSource, name=source_name)

    def _create_stage(self, name: str = INITIAL_STAGE) -> OpportunityStage:
        return self._create_constrained_value_object(OpportunityStage, name=name)

    def _create_priority(self, level_name: str) -> Priority:
        return self._create_constrained_value_object(Priority, level=level_name)

    def _create_constrained_value_object(self, vo_type: type[ValueObjectT], **kwargs) -> ValueObjectT:
        try:
            vo = vo_type(**kwargs)
        except ValueNotAllowed as e:
            raise InvalidData(e.message) from e
        return vo

    def _create_offer(self, offer_items: Iterable[OfferItemCreateUpdateModel]) -> Iterable[OfferItem]:
        offer = (self._create_offer_item(item) for item in offer_items)
        return tuple(offer)

    def _create_offer_item(self, data: OfferItemCreateUpdateModel) -> OfferItem:
        product = Product(name=data.product.name)
        currency = Currency(
            name=data.value.currency.name,
            iso_code=data.value.currency.iso_code,
        )
        try:
            value = Money(currency=currency, amount=data.value.amount)
        except AmountMustBeGreaterThanZero as e:
            raise InvalidData(e.message) from e
        offer_item = OfferItem(product=product, value=value)
        return offer_item

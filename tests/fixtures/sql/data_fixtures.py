from collections.abc import Callable
from decimal import Decimal
from typing import ContextManager

import pytest
from sqlalchemy.orm import Session

from building_blocks.infrastructure.sql.db import Base
from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.command_model import (
    AddressDataCreateUpdateModel,
    CompanyInfoCreateUpdateModel,
    ContactMethodCreateUpdateModel,
    ContactPersonCreateModel,
    CountryCreateUpdateModel,
    CustomerCreateModel,
    LanguageCreateUpdateModel,
)
from customer_management.application.query_model import CustomerReadModel
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.language import Language
from customer_management.infrastructure.sql.customer.models import CountryModel, LanguageModel
from sales.application.lead.command import LeadCommandUseCase
from sales.application.lead.command_model import AssignmentUpdateModel, ContactDataCreateUpdateModel, LeadCreateModel
from sales.application.lead.query_model import LeadReadModel
from sales.application.notes.command_model import NoteCreateModel
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.opportunity.command_model import (
    CurrencyCreateUpdateModel,
    MoneyCreateUpdateModel,
    OfferItemCreateUpdateModel,
    OpportunityCreateModel,
    ProductCreateUpdateModel,
)
from sales.application.opportunity.query_model import OpportunityReadModel, ProductReadModel
from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.application.sales_representative.command_model import SalesRepresentativeCreateModel
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.product import Product
from sales.infrastructure.sql.opportunity.models import CurrencyModel, ProductModel


@pytest.fixture(scope="session")
def representative_1(
    sr_command_use_case: SalesRepresentativeCommandUseCase,
) -> SalesRepresentativeReadModel:
    data = SalesRepresentativeCreateModel(first_name="Jan", last_name="Kowalski")
    sr = sr_command_use_case.create(data=data)
    return sr


@pytest.fixture(scope="session")
def representative_2(
    sr_command_use_case: SalesRepresentativeCommandUseCase,
) -> SalesRepresentativeReadModel:
    data = SalesRepresentativeCreateModel(first_name="Piotr", last_name="Nowak")
    sr = sr_command_use_case.create(data=data)
    return sr


@pytest.fixture(scope="session")
def representative_3(
    sr_command_use_case: SalesRepresentativeCommandUseCase,
) -> SalesRepresentativeReadModel:
    data = SalesRepresentativeCreateModel(first_name="Paweł", last_name="Kowalczyk")
    sr = sr_command_use_case.create(data=data)
    return sr


@pytest.fixture(scope="session")
def country() -> Country:
    return Country(name="Polska", code="pl")


@pytest.fixture(scope="session")
def address(country: Country) -> AddressDataCreateUpdateModel:
    return AddressDataCreateUpdateModel(
        country=CountryCreateUpdateModel(name=country.name, code=country.code),
        street="Street",
        street_no="123",
        postal_code="11222",
        city="City",
    )


@pytest.fixture(scope="session")
def company_info(address: AddressDataCreateUpdateModel) -> CompanyInfoCreateUpdateModel:
    return CompanyInfoCreateUpdateModel(
        name="Company 1",
        industry="automotive",
        size="medium",
        legal_form="limited",
        address=address,
    )


@pytest.fixture(scope="session")
def language() -> Language:
    return Language(name="english", code="en")


@pytest.fixture(scope="session")
def contact_person(language: Language) -> ContactPersonCreateModel:
    contact_method = ContactMethodCreateUpdateModel(type="email", value="email@example.com", is_preferred=True)
    return ContactPersonCreateModel(
        first_name="Jan",
        last_name="Kowalski",
        job_title="CEO",
        preferred_language=LanguageCreateUpdateModel(name=language.name, code=language.code),
        contact_methods=[contact_method],
    )


@pytest.fixture(scope="session")
def customer_1(
    customer_command_use_case: CustomerCommandUseCase,
    representative_1: SalesRepresentativeReadModel,
    company_info: CompanyInfoCreateUpdateModel,
    contact_person: ContactPersonCreateModel,
) -> CustomerReadModel:
    data = CustomerCreateModel(relation_manager_id=representative_1.id, company_info=company_info)
    customer = customer_command_use_case.create(customer_data=data)

    customer_command_use_case.create_contact_person(
        customer_id=customer.id,
        editor_id=customer.relation_manager_id,
        data=contact_person,
    )
    customer_command_use_case.convert(customer_id=customer.id, requestor_id=customer.relation_manager_id)

    return customer


@pytest.fixture(scope="session")
def customer_2(
    customer_command_use_case: CustomerCommandUseCase,
    representative_1: SalesRepresentativeReadModel,
    address: AddressDataCreateUpdateModel,
) -> CustomerReadModel:
    company_info = CompanyInfoCreateUpdateModel(
        name="Company 2",
        industry="agriculture",
        size="small",
        legal_form="partnership",
        address=address,
    )
    data = CustomerCreateModel(relation_manager_id=representative_1.id, company_info=company_info)
    customer = customer_command_use_case.create(customer_data=data)
    return customer


@pytest.fixture(scope="session")
def customer_3(
    customer_command_use_case: CustomerCommandUseCase,
    representative_2: SalesRepresentativeReadModel,
    address: AddressDataCreateUpdateModel,
) -> CustomerReadModel:
    company_info = CompanyInfoCreateUpdateModel(
        name="Company 3",
        industry="technology",
        size="large",
        legal_form="other",
        address=address,
    )
    data = CustomerCreateModel(relation_manager_id=representative_2.id, company_info=company_info)
    customer = customer_command_use_case.create(customer_data=data)
    return customer


@pytest.fixture(scope="session")
def customer_4(
    customer_command_use_case: CustomerCommandUseCase,
    representative_3: SalesRepresentativeReadModel,
    address: AddressDataCreateUpdateModel,
) -> CustomerReadModel:
    company_info = CompanyInfoCreateUpdateModel(
        name="Company 4",
        industry="automotive",
        size="medium",
        legal_form="sole proprietorship",
        address=address,
    )
    data = CustomerCreateModel(relation_manager_id=representative_3.id, company_info=company_info)
    customer = customer_command_use_case.create(customer_data=data)
    return customer


@pytest.fixture(scope="session")
def note_content() -> str:
    return "This is a note"


@pytest.fixture(scope="session")
def lead_1(
    lead_command_use_case: LeadCommandUseCase,
    representative_1: SalesRepresentativeReadModel,
    representative_3: SalesRepresentativeReadModel,
    customer_2: CustomerReadModel,
    note_content: str,
) -> LeadReadModel:
    contact_data = ContactDataCreateUpdateModel(
        first_name="Jan",
        last_name="Kowalski",
        phone="+48123456789",
        email="jan.kowalski@example.com",
    )
    lead_data = LeadCreateModel(customer_id=customer_2.id, source="ads", contact_data=contact_data)
    lead = lead_command_use_case.create(lead_data=lead_data, creator_id=representative_1.id)

    lead_command_use_case.update_assignment(
        lead_id=lead.id,
        requestor_id=lead.created_by_salesman_id,
        assignment_data=AssignmentUpdateModel(new_salesman_id=representative_3.id),
    )
    lead_command_use_case.update_note(
        lead_id=lead.id,
        editor_id=representative_3.id,
        note_data=NoteCreateModel(content=note_content),
    )

    return lead


@pytest.fixture(scope="session")
def lead_2(
    lead_command_use_case: LeadCommandUseCase,
    representative_1: SalesRepresentativeReadModel,
    customer_3: CustomerReadModel,
) -> LeadReadModel:
    contact_data = ContactDataCreateUpdateModel(
        first_name="Piotr",
        last_name="Nowak",
        phone="+48123123456",
        email="piotr.nowak@example.com",
    )
    lead_data = LeadCreateModel(customer_id=customer_3.id, source="cold call", contact_data=contact_data)
    lead = lead_command_use_case.create(lead_data=lead_data, creator_id=representative_1.id)
    return lead


@pytest.fixture(scope="session")
def currency() -> Currency:
    return Currency(name="US dollar", iso_code="USD")


@pytest.fixture(scope="session")
def offer_item(product_1: Product, currency: Currency) -> OfferItemCreateUpdateModel:
    product = ProductCreateUpdateModel(name=product_1.name)
    value = MoneyCreateUpdateModel(
        currency=CurrencyCreateUpdateModel(name=currency.name, iso_code=currency.iso_code), amount=Decimal("100.99")
    )
    return OfferItemCreateUpdateModel(product=product, value=value)


@pytest.fixture(scope="session")
def opportunity_1(
    opportunity_command_use_case: OpportunityCommandUseCase,
    customer_1: CustomerReadModel,
    representative_3: SalesRepresentativeReadModel,
    offer_item: OfferItemCreateUpdateModel,
    note_content: str,
) -> OpportunityReadModel:
    data = OpportunityCreateModel(customer_id=customer_1.id, source="ads", priority="medium", offer=[offer_item])
    opportunity = opportunity_command_use_case.create(data=data, creator_id=representative_3.id)

    opportunity_command_use_case.update_note(
        opportunity_id=opportunity.id,
        editor_id=opportunity.owner_id,
        note_data=NoteCreateModel(content=note_content),
    )

    return opportunity


@pytest.fixture(scope="session")
def opportunity_2(
    opportunity_command_use_case: OpportunityCommandUseCase,
    customer_1: CustomerReadModel,
    representative_1: SalesRepresentativeReadModel,
    offer_item: OfferItemCreateUpdateModel,
) -> OpportunityReadModel:
    data = OpportunityCreateModel(
        customer_id=customer_1.id,
        source="cold call",
        priority="urgent",
        offer=[offer_item],
    )
    opportunity = opportunity_command_use_case.create(data=data, creator_id=representative_1.id)
    return opportunity


@pytest.fixture(scope="session")
def opportunity_3(
    opportunity_command_use_case: OpportunityCommandUseCase,
    customer_1: CustomerReadModel,
    representative_2: SalesRepresentativeReadModel,
    offer_item: OfferItemCreateUpdateModel,
) -> OpportunityReadModel:
    data = OpportunityCreateModel(customer_id=customer_1.id, source="referral", priority="low", offer=[offer_item])
    opportunity = opportunity_command_use_case.create(data=data, creator_id=representative_2.id)
    return opportunity


@pytest.fixture(scope="session")
def product_1() -> Product:
    return Product(name="product 1")


@pytest.fixture(scope="session")
def product_2() -> ProductReadModel:
    return Product(name="product 2")


@pytest.fixture(scope="session", autouse=True)
def create_value_objects_in_db(
    run_migrations: None,
    request: pytest.FixtureRequest,
    session_factory: Callable[[], ContextManager[Session]],
) -> None:
    fixtures_to_models: dict[str, type[Base]] = {
        "product_1": ProductModel,
        "product_2": ProductModel,
        "country": CountryModel,
        "language": LanguageModel,
        "currency": CurrencyModel,
    }
    db_objs = []
    for fixture, model in fixtures_to_models.items():
        value_object = request.getfixturevalue(fixture)
        db_obj = model.from_domain(value_object)
        db_objs.append(db_obj)

    with session_factory() as db:
        db.add_all(db_objs)
        db.commit()

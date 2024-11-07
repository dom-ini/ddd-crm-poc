from datetime import datetime
from decimal import Decimal
from typing import TypeVar
from uuid import uuid4

from sqlalchemy.orm import Session

from building_blocks.infrastructure.sql.config import SQLALCHEMY_DB_URL
from building_blocks.infrastructure.sql.db import Base, DbConnectionManager
from customer_management.infrastructure.sql.customer.models import (
    AddressModel,
    CompanyDataModel,
    ContactMethodModel,
    ContactPersonModel,
    CountryModel,
    CustomerModel,
    LanguageModel,
)
from sales.infrastructure.sql.lead.models import LeadAssignmentEntryModel, LeadModel, LeadNoteModel
from sales.infrastructure.sql.opportunity.models import (
    CurrencyModel,
    OfferItemModel,
    OpportunityModel,
    OpportunityNoteModel,
    ProductModel,
)
from sales.infrastructure.sql.sales_representative.models import SalesRepresentativeModel

EntityT = TypeVar("EntityT", bound=Base)


def save_entities(session: Session, *entities: EntityT) -> None:
    session.add_all(entities)
    session.commit()


def refresh_entities(session: Session, *entities: EntityT) -> None:
    for entity in entities:
        session.refresh(entity)


session_factory = DbConnectionManager.get_session_factory(SQLALCHEMY_DB_URL)

db = session_factory()

# ----------- SALES REPRESENTATIVE

salesman_1 = SalesRepresentativeModel(id="24a9bfa0-42a1-4dd2-ad19-2e26da3c2ce0", first_name="John", last_name="Doe")
salesman_2 = SalesRepresentativeModel(
    id="753bae00-bd6f-4182-ba2f-68942d59d1e6", first_name="Larry", last_name="Jackson"
)
salesman_3 = SalesRepresentativeModel(
    id="54499cbc-5a06-42e9-a850-7607af9c50f0", first_name="Nathan", last_name="Parker"
)
salesman_4 = SalesRepresentativeModel(id="e20f89a5-13a7-416c-b61b-9761f3dafd09", first_name="Maria", last_name="Allen")

all_salesmen = [salesman_1, salesman_2, salesman_3, salesman_4]

save_entities(db, *all_salesmen)
refresh_entities(db, *all_salesmen)

# ----------- CUSTOMER

country_1 = CountryModel(code="pl", name="Poland")
country_2 = CountryModel(code="de", name="Germany")
country_3 = CountryModel(code="no", name="Norway")
country_4 = CountryModel(code="es", name="Spain")

save_entities(db, country_1, country_2, country_3, country_4)

address_1 = AddressModel(
    country_id=country_1.id,
    street="ul. Wiejska",
    street_no="4/6/8",
    postal_code="00-902",
    city="Warsaw",
)
address_2 = AddressModel(
    country_id=country_2.id,
    street="Platz der Republik",
    street_no="1",
    postal_code="11011",
    city="Berlin",
)
address_3 = AddressModel(
    country_id=country_3.id,
    street="Karl Johans gate",
    street_no="22",
    postal_code="0026",
    city="Oslo",
)
address_4 = AddressModel(
    country_id=country_4.id,
    street="Plaza de las Cortes",
    street_no="1",
    postal_code="28014",
    city="Madrid",
)

save_entities(db, address_1, address_2, address_3, address_4)

customer_1 = CustomerModel(
    id=str(uuid4()),
    relation_manager_id=salesman_1.id,
    status_name="initial",
)
customer_2 = CustomerModel(
    id=str(uuid4()),
    relation_manager_id=salesman_2.id,
    status_name="converted",
)
customer_3 = CustomerModel(
    id=str(uuid4()),
    relation_manager_id=salesman_3.id,
    status_name="converted",
)
customer_4 = CustomerModel(
    id=str(uuid4()),
    relation_manager_id=salesman_4.id,
    status_name="archived",
)

save_entities(db, customer_1, customer_2, customer_3, customer_4)

company_data_1 = CompanyDataModel(
    address_id=address_1.id,
    customer_id=customer_1.id,
    name="Polska Spółka Rolnicza S.A.",
    industry_name="agriculture",
    size="large",
    legal_form="joint-stock",
)
company_data_2 = CompanyDataModel(
    address_id=address_2.id,
    customer_id=customer_2.id,
    name="Deutches Automobileunternehmen GmbH",
    industry_name="automotive",
    size="medium",
    legal_form="limited",
)
company_data_3 = CompanyDataModel(
    address_id=address_3.id,
    customer_id=customer_3.id,
    name="Norsk Frakt",
    industry_name="transportation & logistics",
    size="small",
    legal_form="partnership",
)
company_data_4 = CompanyDataModel(
    address_id=address_4.id,
    customer_id=customer_4.id,
    name="Ventas en España",
    industry_name="retail",
    size="micro",
    legal_form="sole proprietorship",
)

save_entities(db, company_data_1, company_data_2, company_data_3, company_data_4)
refresh_entities(db, customer_1, customer_2, customer_3, customer_4)

language_1 = LanguageModel(code="pl", name="Polish")
language_2 = LanguageModel(code="de", name="German")
language_3 = LanguageModel(code="no", name="Norwegian (bokmål)")
language_4 = LanguageModel(code="es", name="Spanish")

save_entities(db, language_1, language_2, language_3, language_4)

contact_person_1 = ContactPersonModel(
    id=str(uuid4()),
    customer_id=customer_1.id,
    language_id=language_1.id,
    first_name="Jan",
    last_name="Kowalski",
    job_title="CEO",
)
contact_person_2 = ContactPersonModel(
    id=str(uuid4()),
    customer_id=customer_2.id,
    language_id=language_2.id,
    first_name="Max",
    last_name="Mustermann",
    job_title="sales coordinator",
)
contact_person_3 = ContactPersonModel(
    id=str(uuid4()),
    customer_id=customer_3.id,
    language_id=language_3.id,
    first_name="Ola",
    last_name="Nordmann",
    job_title="partner",
)
contact_person_4 = ContactPersonModel(
    id=str(uuid4()),
    customer_id=customer_4.id,
    language_id=language_4.id,
    first_name="Juana",
    last_name="Pérez",
    job_title="owner",
)

save_entities(db, contact_person_1, contact_person_2, contact_person_3, contact_person_4)

contact_method_1 = ContactMethodModel(
    contact_person_id=contact_person_1.id,
    value="+48123456789",
    type="phone",
    is_preferred=True,
)
contact_method_2 = ContactMethodModel(
    contact_person_id=contact_person_2.id,
    value="max.mustermann@example.com",
    type="email",
    is_preferred=True,
)
contact_method_3 = ContactMethodModel(
    contact_person_id=contact_person_3.id,
    value="ola.nordmann@example.com",
    type="email",
    is_preferred=True,
)
contact_method_4 = ContactMethodModel(
    contact_person_id=contact_person_4.id,
    value="juana.perez@example.com",
    type="email",
    is_preferred=True,
)

save_entities(db, contact_method_1, contact_method_2, contact_method_3, contact_method_4)

# ----------- LEAD

lead_1 = LeadModel(
    id=str(uuid4()),
    created_at=datetime.now(),
    source_name="ads",
    contact_data_first_name=contact_person_1.first_name,
    contact_data_last_name=contact_person_1.last_name,
    contact_data_phone=contact_method_1.value,
    customer_id=customer_1.id,
    created_by_id=salesman_1.id,
)
lead_2 = LeadModel(
    id=str(uuid4()),
    created_at=datetime.now(),
    source_name="social media",
    contact_data_first_name=contact_person_2.first_name,
    contact_data_last_name=contact_person_2.last_name,
    contact_data_email=contact_method_2.value,
    customer_id=customer_2.id,
    created_by_id=salesman_2.id,
)
lead_3 = LeadModel(
    id=str(uuid4()),
    created_at=datetime.now(),
    source_name="website",
    contact_data_first_name=contact_person_3.first_name,
    contact_data_last_name=contact_person_3.last_name,
    contact_data_email=contact_method_3.value,
    customer_id=customer_3.id,
    created_by_id=salesman_3.id,
)
lead_4 = LeadModel(
    id=str(uuid4()),
    created_at=datetime.now(),
    source_name="referral",
    contact_data_first_name=contact_person_4.first_name,
    contact_data_last_name=contact_person_4.last_name,
    contact_data_email=contact_method_4.value,
    customer_id=customer_4.id,
    created_by_id=salesman_4.id,
)

save_entities(db, lead_1, lead_2, lead_3, lead_4)
refresh_entities(db, lead_1, lead_2, lead_3, lead_4)

lead_note_1 = LeadNoteModel(
    lead_id=lead_2.id,
    created_by_id=salesman_2.id,
    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    created_at=datetime.now(),
)
lead_note_2 = LeadNoteModel(
    lead_id=lead_3.id,
    created_by_id=salesman_3.id,
    content="Mauris tristique hendrerit ultrices. Sed ac sapien fringilla ante porttitor porta.",
    created_at=datetime.now(),
)
lead_note_3 = LeadNoteModel(
    lead_id=lead_4.id,
    created_by_id=salesman_4.id,
    content="Proin eget dui iaculis ligula congue hendrerit quis in orci.",
    created_at=datetime.now(),
)

save_entities(db, lead_note_1, lead_note_2, lead_note_3)

lead_assignment_1 = LeadAssignmentEntryModel(
    lead_id=lead_2.id,
    previous_owner_id=None,
    new_owner_id=salesman_2.id,
    assigned_by_id=salesman_2.id,
    assigned_at=datetime.now(),
)
lead_assignment_2 = LeadAssignmentEntryModel(
    lead_id=lead_3.id,
    previous_owner_id=None,
    new_owner_id=salesman_3.id,
    assigned_by_id=salesman_3.id,
    assigned_at=datetime.now(),
)
lead_assignment_3 = LeadAssignmentEntryModel(
    lead_id=lead_4.id,
    previous_owner_id=None,
    new_owner_id=salesman_4.id,
    assigned_by_id=salesman_4.id,
    assigned_at=datetime.now(),
)

save_entities(db, lead_assignment_1, lead_assignment_2, lead_assignment_3)

# ----------- OPPORTUNITY

product_1 = ProductModel(name="Some product")
product_2 = ProductModel(name="Some service")
product_3 = ProductModel(name="Some other service")

save_entities(db, product_1, product_2, product_3)
refresh_entities(db, product_1, product_2, product_3)

currency_1 = CurrencyModel(name="Euro", iso_code="EUR")
currency_2 = CurrencyModel(name="Norwegian krone", iso_code="NOK")
currency_3 = CurrencyModel(name="U.S. dollar", iso_code="USD")

save_entities(db, currency_1, currency_2, currency_3)
refresh_entities(db, currency_1, currency_2, currency_3)

opportunity_1 = OpportunityModel(
    id=str(uuid4()),
    created_by_id=salesman_2.id,
    created_at=datetime.now(),
    customer_id=customer_2.id,
    owner_id=salesman_2.id,
    source_name="cold call",
    stage_name="qualification",
    priority_level="low",
)
opportunity_2 = OpportunityModel(
    id=str(uuid4()),
    created_by_id=salesman_3.id,
    created_at=datetime.now(),
    customer_id=customer_3.id,
    owner_id=salesman_3.id,
    source_name="ads",
    stage_name="proposal",
    priority_level="medium",
)
opportunity_3 = OpportunityModel(
    id=str(uuid4()),
    created_by_id=salesman_4.id,
    created_at=datetime.now(),
    customer_id=customer_4.id,
    owner_id=salesman_4.id,
    source_name="event",
    stage_name="closed-won",
    priority_level="high",
)

save_entities(db, opportunity_1, opportunity_2, opportunity_3)

offer_item_1 = OfferItemModel(
    opportunity_id=opportunity_1.id,
    product_id=product_1.id,
    currency_id=currency_1.id,
    amount=Decimal("1999.99"),
)
offer_item_2 = OfferItemModel(
    opportunity_id=opportunity_2.id,
    product_id=product_2.id,
    currency_id=currency_2.id,
    amount=Decimal("399.99"),
)
offer_item_3 = OfferItemModel(
    opportunity_id=opportunity_3.id,
    product_id=product_3.id,
    currency_id=currency_3.id,
    amount=Decimal("399.99"),
)

save_entities(db, offer_item_1, offer_item_2, offer_item_3)

opportunity_note_1 = OpportunityNoteModel(
    opportunity_id=opportunity_1.id,
    created_by_id=salesman_2.id,
    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    created_at=datetime.now(),
)
opportunity_note_2 = OpportunityNoteModel(
    opportunity_id=opportunity_2.id,
    created_by_id=salesman_3.id,
    content="Aliquam interdum commodo nisl, sit amet venenatis justo tristique vitae.",
    created_at=datetime.now(),
)
opportunity_note_3 = OpportunityNoteModel(
    opportunity_id=opportunity_3.id,
    created_by_id=salesman_4.id,
    content="Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae.",
    created_at=datetime.now(),
)

save_entities(db, opportunity_note_1, opportunity_note_2, opportunity_note_3)

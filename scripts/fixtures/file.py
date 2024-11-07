from decimal import Decimal
from shelve import Shelf
from typing import Any
from uuid import uuid4

from building_blocks.infrastructure.file.io import get_write_db
from customer_management.domain.entities.customer.customer import Customer
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.company_segment import CompanySegment
from customer_management.domain.value_objects.contact_method import ContactMethod
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.industry import Industry
from customer_management.domain.value_objects.language import Language
from customer_management.infrastructure.file.config import COUNTRIES_PATH, CUSTOMERS_PATH, LANGUAGES_PATH
from sales.domain.entities.lead import Lead
from sales.domain.entities.opportunity import Opportunity
from sales.domain.entities.sales_representative import SalesRepresentative
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.money.money import Money
from sales.domain.value_objects.offer_item import OfferItem
from sales.domain.value_objects.opportunity_stage import OpportunityStage
from sales.domain.value_objects.priority import Priority
from sales.domain.value_objects.product import Product
from sales.infrastructure.file.config import CURRENCIES_PATH, LEAD_PATH, PRODUCTS_PATH, SALES_REPR_PATH


def save(db: Shelf, *entities: Any) -> None:
    for entity in entities:
        key = entity.id if hasattr(entity, "id") else str(uuid4())
        db[key] = entity
    db.sync()


# ----------- SALES REPRESENTATIVE

representative_1 = SalesRepresentative(id="24a9bfa0-42a1-4dd2-ad19-2e26da3c2ce0", first_name="John", last_name="Doe")
representative_2 = SalesRepresentative(
    id="753bae00-bd6f-4182-ba2f-68942d59d1e6", first_name="Larry", last_name="Jackson"
)
representative_3 = SalesRepresentative(
    id="54499cbc-5a06-42e9-a850-7607af9c50f0", first_name="Nathan", last_name="Parker"
)
representative_4 = SalesRepresentative(id="e20f89a5-13a7-416c-b61b-9761f3dafd09", first_name="Maria", last_name="Allen")

# ----------- CUSTOMER

country_1 = Country(code="pl", name="Poland")
country_2 = Country(code="de", name="Germany")
country_3 = Country(code="no", name="Norway")
country_4 = Country(code="es", name="Spain")

language_1 = Language(code="pl", name="Polish")
language_2 = Language(code="de", name="German")
language_3 = Language(code="no", name="Norwegian (bokmål)")
language_4 = Language(code="es", name="Spanish")

address_1 = Address(
    country=country_1,
    street="ul. Wiejska",
    street_no="4/6/8",
    postal_code="00-902",
    city="Warsaw",
)
address_2 = Address(
    country=country_2,
    street="Platz der Republik",
    street_no="1",
    postal_code="11011",
    city="Berlin",
)
address_3 = Address(
    country=country_3,
    street="Karl Johans gate",
    street_no="22",
    postal_code="0026",
    city="Oslo",
)
address_4 = Address(
    country=country_4,
    street="Plaza de las Cortes",
    street_no="1",
    postal_code="28014",
    city="Madrid",
)

industry_1 = Industry(name="agriculture")
industry_2 = Industry(name="automotive")
industry_3 = Industry(name="transportation & logistics")
industry_4 = Industry(name="retail")

segment_1 = CompanySegment(size="large", legal_form="joint-stock")
segment_2 = CompanySegment(size="medium", legal_form="limited")
segment_3 = CompanySegment(size="small", legal_form="partnership")
segment_4 = CompanySegment(size="micro", legal_form="sole proprietorship")

company_info_1 = CompanyInfo(
    name="Polska Spółka Rolnicza S.A.",
    industry=industry_1,
    segment=segment_1,
    address=address_1,
)
company_info_2 = CompanyInfo(
    name="Deutches Automobileunternehmen GmbH",
    industry=industry_2,
    segment=segment_2,
    address=address_2,
)
company_info_3 = CompanyInfo(
    name="Norsk Frakt",
    industry=industry_3,
    segment=segment_3,
    address=address_3,
)
company_info_4 = CompanyInfo(
    name="Ventas en España",
    industry=industry_4,
    segment=segment_4,
    address=address_4,
)

customer_1 = Customer(id=str(uuid4()), company_info=company_info_1, relation_manager_id=representative_1.id)
customer_2 = Customer(id=str(uuid4()), company_info=company_info_2, relation_manager_id=representative_2.id)
customer_3 = Customer(id=str(uuid4()), company_info=company_info_3, relation_manager_id=representative_3.id)
customer_4 = Customer(id=str(uuid4()), company_info=company_info_4, relation_manager_id=representative_4.id)

contact_method_1 = ContactMethod(type="phone", value="+48123456789", is_preferred=True)
contact_method_2 = ContactMethod(type="email", value="max.mustermann@example.com", is_preferred=True)
contact_method_3 = ContactMethod(type="email", value="ola.nordmann@example.com", is_preferred=True)
contact_method_4 = ContactMethod(type="email", value="juana.perez@example.com", is_preferred=True)

customer_1.add_contact_person(
    editor_id=customer_1.relation_manager_id,
    contact_person_id=str(uuid4()),
    first_name="Jan",
    last_name="Kowalski",
    job_title="CEO",
    preferred_language=language_1,
    contact_methods=(contact_method_1,),
)
customer_2.add_contact_person(
    editor_id=customer_2.relation_manager_id,
    contact_person_id=str(uuid4()),
    first_name="Max",
    last_name="Mustermann",
    job_title="sales coordinator",
    preferred_language=language_2,
    contact_methods=(contact_method_2,),
)
customer_3.add_contact_person(
    editor_id=customer_3.relation_manager_id,
    contact_person_id=str(uuid4()),
    first_name="Ola",
    last_name="Nordmann",
    job_title="partner",
    preferred_language=language_3,
    contact_methods=(contact_method_3,),
)
customer_4.add_contact_person(
    editor_id=customer_4.relation_manager_id,
    contact_person_id=str(uuid4()),
    first_name="Juana",
    last_name="Pérez",
    job_title="owner",
    preferred_language=language_4,
    contact_methods=(contact_method_4,),
)

# ----------- LEAD

source_1 = AcquisitionSource(name="ads")
source_2 = AcquisitionSource(name="social media")
source_3 = AcquisitionSource(name="website")
source_4 = AcquisitionSource(name="referral")

contact_data_1 = ContactData(
    first_name=customer_1.contact_persons[0].first_name,
    last_name=customer_1.contact_persons[0].last_name,
    phone=customer_1.contact_persons[0].contact_methods[0].value,
)
contact_data_2 = ContactData(
    first_name=customer_2.contact_persons[0].first_name,
    last_name=customer_2.contact_persons[0].last_name,
    email=customer_2.contact_persons[0].contact_methods[0].value,
)
contact_data_3 = ContactData(
    first_name=customer_3.contact_persons[0].first_name,
    last_name=customer_3.contact_persons[0].last_name,
    email=customer_3.contact_persons[0].contact_methods[0].value,
)
contact_data_4 = ContactData(
    first_name=customer_4.contact_persons[0].first_name,
    last_name=customer_4.contact_persons[0].last_name,
    email=customer_4.contact_persons[0].contact_methods[0].value,
)

lead_1 = Lead.make(
    id=str(uuid4()),
    customer_id=customer_1.id,
    created_by_salesman_id=representative_1.id,
    contact_data=contact_data_1,
    source=source_1,
)
lead_2 = Lead.make(
    id=str(uuid4()),
    customer_id=customer_2.id,
    created_by_salesman_id=representative_2.id,
    contact_data=contact_data_2,
    source=source_2,
)
lead_3 = Lead.make(
    id=str(uuid4()),
    customer_id=customer_3.id,
    created_by_salesman_id=representative_3.id,
    contact_data=contact_data_3,
    source=source_3,
)
lead_4 = Lead.make(
    id=str(uuid4()),
    customer_id=customer_4.id,
    created_by_salesman_id=representative_4.id,
    contact_data=contact_data_4,
    source=source_4,
)

lead_2.assign_salesman(new_salesman_id=representative_2.id, requestor_id=representative_2.id)
lead_3.assign_salesman(new_salesman_id=representative_3.id, requestor_id=representative_3.id)
lead_4.assign_salesman(new_salesman_id=representative_4.id, requestor_id=representative_4.id)

lead_2.change_note(
    new_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    editor_id=representative_2.id,
)
lead_3.change_note(
    new_content="Mauris tristique hendrerit ultrices. Sed ac sapien fringilla ante porttitor porta.",
    editor_id=representative_3.id,
)
lead_4.change_note(
    new_content="Proin eget dui iaculis ligula congue hendrerit quis in orci.",
    editor_id=representative_4.id,
)

# ----------- OPPORTUNITY

product_1 = Product(name="Some product")
product_2 = Product(name="Some service")
product_3 = Product(name="Some other service")

currency_1 = Currency(name="Euro", iso_code="EUR")
currency_2 = Currency(name="Norwegian krone", iso_code="NOK")
currency_3 = Currency(name="U.S. dollar", iso_code="USD")

op_source_1 = AcquisitionSource(name="cold call")
op_source_2 = AcquisitionSource(name="ads")
op_source_3 = AcquisitionSource(name="event")

stage_1 = OpportunityStage(name="qualification")
stage_2 = OpportunityStage(name="proposal")
stage_3 = OpportunityStage(name="closed-won")

priority_1 = Priority(level="low")
priority_2 = Priority(level="medium")
priority_3 = Priority(level="high")

money_1 = Money(currency=currency_1, amount=Decimal("1999.99"))
money_2 = Money(currency=currency_2, amount=Decimal("399.99"))
money_3 = Money(currency=currency_3, amount=Decimal("399.99"))

offer_item_1 = OfferItem(product=product_1, value=money_1)
offer_item_2 = OfferItem(product=product_2, value=money_2)
offer_item_3 = OfferItem(product=product_3, value=money_3)

opportunity_1 = Opportunity.make(
    id=str(uuid4()),
    source=op_source_1,
    stage=stage_1,
    priority=priority_1,
    created_by_id=representative_2.id,
    customer_id=customer_2.id,
    offer=(offer_item_1,),
)
opportunity_2 = Opportunity.make(
    id=str(uuid4()),
    source=op_source_2,
    stage=stage_2,
    priority=priority_2,
    created_by_id=representative_3.id,
    customer_id=customer_3.id,
    offer=(offer_item_2,),
)
opportunity_3 = Opportunity.make(
    id=str(uuid4()),
    source=op_source_3,
    stage=stage_3,
    priority=priority_3,
    created_by_id=representative_4.id,
    customer_id=customer_4.id,
    offer=(offer_item_3,),
)

opportunity_1.change_note(
    new_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    editor_id=representative_2.id,
)
opportunity_2.change_note(
    new_content="Aliquam interdum commodo nisl, sit amet venenatis justo tristique vitae.",
    editor_id=representative_3.id,
)
opportunity_3.change_note(
    new_content="Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae.",
    editor_id=representative_4.id,
)

# ----------- MANIPULATE DOMAIN OBJECTS

customer_2.convert(requestor_id=representative_2.id)
customer_3.convert(requestor_id=representative_3.id)
customer_4.convert(requestor_id=representative_4.id)

customer_4.archive(requestor_id=representative_4.id)

# ----------- SAVE DATA

sr_db = get_write_db(SALES_REPR_PATH)
save(sr_db, representative_1, representative_2, representative_3, representative_4)
sr_db.close()

countries_db = get_write_db(COUNTRIES_PATH)
save(countries_db, country_1, country_2, country_3, country_4)
countries_db.close()

languages_db = get_write_db(LANGUAGES_PATH)
save(languages_db, language_1, language_2, language_3, language_4)
languages_db.close()

customers_db = get_write_db(CUSTOMERS_PATH)
save(customers_db, customer_1, customer_2, customer_3, customer_4)
customers_db.close()

leads_db = get_write_db(LEAD_PATH)
save(leads_db, lead_1, lead_2, lead_3, lead_4)
leads_db.close()

products_db = get_write_db(PRODUCTS_PATH)
save(products_db, product_1, product_2, product_3)
products_db.close()

currencies_db = get_write_db(CURRENCIES_PATH)
save(currencies_db, currency_1, currency_2, currency_3)
currencies_db.close()

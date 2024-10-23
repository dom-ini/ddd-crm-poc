from typing import Self

from faker import Faker
from pydantic import Field

from building_blocks.application.nested_model import NestedModel
from building_blocks.application.query_model import BaseReadModel
from customer_management.domain.entities.contact_person import ContactPerson
from customer_management.domain.entities.customer import Customer
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.company_segment import ALLOWED_COMPANY_SIZES, ALLOWED_LEGAL_FORMS
from customer_management.domain.value_objects.contact_method import ALLOWED_CONTACT_TYPES, ContactMethod
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.customer_status import CustomerStatusName
from customer_management.domain.value_objects.industry import ALLOWED_INDUSTRY_NAMES
from customer_management.domain.value_objects.language import Language

faker = Faker(locale="pl_PL")


class CountryReadModel(BaseReadModel[Country], NestedModel):
    code: str = Field(examples=[faker.country_code()])
    name: str = Field(examples=[faker.country()])

    @classmethod
    def from_domain(cls, entity: Country) -> Self:
        return cls(
            code=entity.code,
            name=entity.name,
        )


class CompanyAddressReadModel(BaseReadModel[Address], NestedModel):
    country: str = Field(examples=[faker.country()])
    street: str = Field(examples=[faker.street_name()])
    street_no: str = Field(examples=[faker.building_number()])
    postal_code: str = Field(examples=[faker.postalcode()])
    city: str = Field(examples=[faker.city()])

    @classmethod
    def from_domain(cls, entity: Address) -> Self:
        return cls(
            country=entity.country.name,
            street=entity.street,
            street_no=entity.street_no,
            postal_code=entity.postal_code,
            city=entity.city,
        )


class CompanyInfoReadModel(BaseReadModel[CompanyInfo], NestedModel):
    name: str = Field(examples=[faker.company()])
    industry: str = Field(examples=ALLOWED_INDUSTRY_NAMES)
    size: str = Field(examples=ALLOWED_COMPANY_SIZES)
    legal_form: str = Field(examples=ALLOWED_LEGAL_FORMS)
    address: CompanyAddressReadModel = Field(examples=[CompanyAddressReadModel.get_examples()])

    @classmethod
    def from_domain(cls, entity: CompanyInfo) -> Self:
        return cls(
            name=entity.name,
            industry=entity.industry.name,
            size=entity.segment.size,
            legal_form=entity.segment.legal_form,
            address=CompanyAddressReadModel.from_domain(entity.address),
        )


class CustomerReadModel(BaseReadModel[Customer]):
    id: str = Field(examples=[faker.uuid4()])
    relation_manager_id: str = Field(examples=[faker.uuid4()])
    status: str = Field(examples=[status.value for status in CustomerStatusName])
    company_info: CompanyInfoReadModel = Field(examples=[CompanyInfoReadModel.get_examples()])

    @classmethod
    def from_domain(cls, entity: Customer) -> Self:
        return cls(
            id=entity.id,
            relation_manager_id=entity.relation_manager_id,
            status=entity.status,
            company_info=CompanyInfoReadModel.from_domain(entity.company_info),
        )


class ContactMethodReadModel(BaseReadModel[ContactMethod], NestedModel):
    type: str = Field(examples=ALLOWED_CONTACT_TYPES)
    value: str = Field(examples=[faker.email(), faker.phone_number()])
    is_preferred: bool = Field(examples=[faker.boolean()])

    @classmethod
    def from_domain(cls, entity: ContactMethod) -> Self:
        return cls(type=entity.type, value=entity.value, is_preferred=entity.is_preferred)


class LanguageReadModel(BaseReadModel[Language], NestedModel):
    name: str = Field(examples=["Polish"])
    code: str = Field(examples=["pl"])

    @classmethod
    def from_domain(cls, entity: Language) -> Self:
        return cls(name=entity.name, code=entity.code)


class ContactPersonReadModel(BaseReadModel[ContactPerson]):
    id: str = Field(examples=[faker.uuid4()])
    first_name: str = Field(examples=[faker.first_name()])
    last_name: str = Field(examples=[faker.last_name()])
    job_title: str = Field(examples=[faker.job()])
    preferred_language: LanguageReadModel = Field(examples=[LanguageReadModel.get_examples()])
    contact_methods: list[ContactMethodReadModel] = Field(examples=[[ContactMethodReadModel.get_examples()]])

    @classmethod
    def from_domain(cls, entity: ContactPerson) -> Self:
        return cls(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            job_title=entity.job_title,
            preferred_language=LanguageReadModel.from_domain(entity.preferred_language),
            contact_methods=[ContactMethodReadModel.from_domain(method) for method in entity.contact_methods],
        )

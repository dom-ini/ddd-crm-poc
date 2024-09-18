from faker import Faker
from pydantic import Field
from building_blocks.application.command_model import BaseCommandModel
from building_blocks.application.nested_model import NestedModel
from customer_management.domain.value_objects.company_segment import (
    ALLOWED_COMPANY_SIZES,
    ALLOWED_LEGAL_FORMS,
)
from customer_management.domain.value_objects.industry import ALLOWED_INDUSTRY_NAMES
from customer_management.domain.value_objects.contact_method import (
    ALLOWED_CONTACT_TYPES,
)

faker = Faker(locale="pl_PL")


class CountryCreateUpdateModel(BaseCommandModel, NestedModel):
    name: str = Field(examples=["Polska"])
    code: str = Field(examples=["PL"])


class AddressDataCreateUpdateModel(BaseCommandModel, NestedModel):
    country: CountryCreateUpdateModel = Field(
        examples=[CountryCreateUpdateModel.get_examples()]
    )
    street: str = Field(examples=[faker.street_name()])
    street_no: str = Field(examples=[faker.building_number()])
    postal_code: str = Field(examples=[faker.postalcode()])
    city: str = Field(examples=[faker.city()])


class CompanyInfoCreateUpdateModel(BaseCommandModel, NestedModel):
    name: str = Field(examples=[faker.company()])
    industry: str = Field(examples=ALLOWED_INDUSTRY_NAMES)
    size: str = Field(examples=ALLOWED_COMPANY_SIZES)
    legal_form: str = Field(examples=ALLOWED_LEGAL_FORMS)
    address: AddressDataCreateUpdateModel = Field(
        examples=[AddressDataCreateUpdateModel.get_examples()]
    )


class CustomerCreateModel(BaseCommandModel):
    relation_manager_id: str = Field(examples=[faker.uuid4()])
    company_info: CompanyInfoCreateUpdateModel = Field(
        examples=[CompanyInfoCreateUpdateModel.get_examples()]
    )


class CustomerUpdateModel(BaseCommandModel):
    relation_manager_id: str | None = Field(default=None, examples=[faker.uuid4()])
    company_info: CompanyInfoCreateUpdateModel | None = Field(
        default=None, examples=[CompanyInfoCreateUpdateModel.get_examples()]
    )


class LanguageCreateUpdateModel(BaseCommandModel, NestedModel):
    name: str = Field(examples=["Polish"])
    code: str = Field(examples=["pl"])


class ContactMethodCreateUpdateModel(BaseCommandModel, NestedModel):
    type: str = Field(examples=ALLOWED_CONTACT_TYPES)
    value: str = Field(examples=[faker.email(), faker.phone_number()])
    is_preferred: bool = Field(examples=[faker.boolean()])


class ContactPersonCreateModel(BaseCommandModel):
    first_name: str = Field(examples=[faker.first_name()])
    last_name: str = Field(examples=[faker.last_name()])
    job_title: str = Field(examples=[faker.job()])
    preferred_language: LanguageCreateUpdateModel = Field(
        examples=[LanguageCreateUpdateModel.get_examples()]
    )
    contact_methods: list[ContactMethodCreateUpdateModel] = Field(
        examples=[[ContactMethodCreateUpdateModel.get_examples()]]
    )


class ContactPersonUpdateModel(BaseCommandModel):
    first_name: str | None = Field(default=None, examples=[faker.first_name()])
    last_name: str | None = Field(default=None, examples=[faker.last_name()])
    job_title: str | None = Field(default=None, examples=[faker.job()])
    preferred_language: LanguageCreateUpdateModel | None = Field(
        default=None, examples=[LanguageCreateUpdateModel.get_examples()]
    )
    contact_methods: list[ContactMethodCreateUpdateModel] | None = Field(
        default=None, examples=[[ContactMethodCreateUpdateModel.get_examples()]]
    )

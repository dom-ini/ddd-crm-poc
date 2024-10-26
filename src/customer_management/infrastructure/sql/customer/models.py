from types import SimpleNamespace
from typing import Any, Self

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from building_blocks.infrastructure.sql.db import Base
from building_blocks.infrastructure.sql.utils import generate_uuid
from customer_management.domain.entities.contact_person.contact_person import ContactPerson
from customer_management.domain.entities.customer import Customer
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.company_info import CompanyInfo
from customer_management.domain.value_objects.company_segment import CompanySegment
from customer_management.domain.value_objects.contact_method import ContactMethod
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.industry import Industry
from customer_management.domain.value_objects.language import Language


class CountryModel(Base[Country]):
    __tablename__ = "country"

    id: Mapped[str] = mapped_column(default=generate_uuid, primary_key=True, index=True)

    code: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def to_domain(self) -> Country:
        return Country(code=self.code, name=self.name)

    @classmethod
    def from_domain(cls, entity: Country, **kwargs: Any) -> Self:
        return cls(
            code=entity.code,
            name=entity.name,
        )


class AddressModel(Base[Address]):
    __tablename__ = "address"

    id: Mapped[str] = mapped_column(default=generate_uuid, primary_key=True, index=True)
    country_id: Mapped[str] = mapped_column(ForeignKey("country.id"), nullable=False, index=True)

    street: Mapped[str] = mapped_column(nullable=False)
    street_no: Mapped[str] = mapped_column(nullable=False)
    postal_code: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)

    country: Mapped["CountryModel"] = relationship()

    def to_domain(self) -> Address:
        return Address(
            country=self.country.to_domain(),
            street=self.street,
            street_no=self.street_no,
            postal_code=self.postal_code,
            city=self.city,
        )

    @classmethod
    def from_domain(cls, entity: Address, **kwargs: str) -> Self:
        return cls(
            country_id=kwargs["country_id"],
            street=entity.street,
            street_no=entity.street_no,
            postal_code=entity.postal_code,
            city=entity.city,
        )


class CompanyDataModel(Base[CompanyInfo]):
    __tablename__ = "company_data"

    id: Mapped[str] = mapped_column(default=generate_uuid, primary_key=True, index=True)
    address_id: Mapped[str] = mapped_column(ForeignKey("address.id"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(nullable=False)
    industry_name: Mapped[str] = mapped_column(nullable=False)
    size: Mapped[str] = mapped_column(nullable=False)
    legal_form: Mapped[str] = mapped_column(nullable=False)

    address: Mapped["AddressModel"] = relationship(backref="customer")
    customer: Mapped["CustomerModel"] = relationship(back_populates="company_data")

    @hybrid_property
    def industry(self) -> SimpleNamespace:
        return SimpleNamespace(name=self.industry_name)

    @hybrid_property
    def segment(self) -> SimpleNamespace:
        return SimpleNamespace(size=self.size, legal_form=self.legal_form)

    def to_domain(self) -> CompanyInfo:
        industry = Industry(name=self.industry_name)
        segment = CompanySegment(size=self.size, legal_form=self.legal_form)
        return CompanyInfo(
            name=self.name,
            industry=industry,
            segment=segment,
            address=self.address.to_domain(),
        )

    @classmethod
    def from_domain(cls, entity: CompanyInfo, **kwargs: str) -> Self:
        return cls(
            address_id=kwargs["address_id"],
            customer_id=kwargs["customer_id"],
            name=entity.name,
            industry_name=entity.industry.name,
            size=entity.segment.size,
            legal_form=entity.segment.legal_form,
        )


class LanguageModel(Base[Language]):
    __tablename__ = "language"

    id: Mapped[str] = mapped_column(default=generate_uuid, primary_key=True, index=True)

    code: Mapped[str] = mapped_column(String(2), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def to_domain(self) -> Language:
        return Language(code=self.code, name=self.name)

    @classmethod
    def from_domain(cls, entity: Language, **kwargs: Any) -> Self:
        return cls(
            code=entity.code,
            name=entity.name,
        )


class ContactMethodModel(Base[ContactMethod]):
    __tablename__ = "contact_method"

    contact_person_id = mapped_column(ForeignKey("contact_person.id"), nullable=False, index=True, primary_key=True)

    value: Mapped[str] = mapped_column(nullable=False, unique=True, primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    is_preferred: Mapped[bool] = mapped_column(nullable=False)

    contact_person: Mapped["ContactPersonModel"] = relationship(back_populates="contact_methods")

    def to_domain(self) -> ContactMethod:
        return ContactMethod(type=self.type, value=self.value, is_preferred=self.is_preferred)

    @classmethod
    def from_domain(cls, entity: ContactMethod, **kwargs: str) -> Self:
        return cls(
            contact_person_id=kwargs["contact_person_id"],
            value=entity.value,
            type=entity.type,
            is_preferred=entity.is_preferred,
        )


class ContactPersonModel(Base[ContactPerson]):
    __tablename__ = "contact_person"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    language_id: Mapped[str] = mapped_column(ForeignKey("language.id"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.id"), nullable=False, index=True)

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    job_title: Mapped[str] = mapped_column(nullable=False)

    language: Mapped["LanguageModel"] = relationship()
    contact_methods: Mapped[list["ContactMethodModel"]] = relationship(
        back_populates="contact_person", cascade="all, delete-orphan"
    )

    def to_domain(self) -> ContactPerson:
        contact_methods = tuple(method.to_domain() for method in self.contact_methods)
        return ContactPerson(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            job_title=self.job_title,
            preferred_language=self.language.to_domain(),
            contact_methods=contact_methods,
        )

    @classmethod
    def from_domain(cls, entity: ContactPerson, **kwargs: Any) -> Self:
        return cls(
            id=entity.id,
            language_id=kwargs["language_id"],
            customer_id=kwargs["customer_id"],
            first_name=entity.first_name,
            last_name=entity.last_name,
            job_title=entity.job_title,
        )


class CustomerModel(Base[Customer]):
    __tablename__ = "customer"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    relation_manager_id: Mapped[str] = mapped_column(nullable=False, index=True)

    status_name: Mapped[str] = mapped_column(nullable=False)

    company_data: Mapped["CompanyDataModel"] = relationship(back_populates="customer", lazy="selectin")
    contact_persons: Mapped[list["ContactPersonModel"]] = relationship(backref="customer")

    @hybrid_property
    def company_info(self) -> "CompanyDataModel":
        return self.company_data

    @hybrid_property
    def status(self) -> SimpleNamespace:
        return SimpleNamespace(name=self.status_name)

    def to_domain(self) -> Customer:
        contact_persons = tuple(person.to_domain() for person in self.contact_persons)

        return Customer.reconstitute(
            id=self.id,
            relation_manager_id=self.relation_manager_id,
            status=self.status_name,
            company_info=self.company_data.to_domain(),
            contact_persons=contact_persons,
        )

    @classmethod
    def from_domain(cls, entity: Customer, **kwargs: Any) -> Self:
        return cls(
            id=entity.id,
            relation_manager_id=entity.relation_manager_id,
            status_name=entity.status,
        )

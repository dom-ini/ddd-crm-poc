from abc import ABC, abstractmethod


class BaseDTO[DomainModel, ReadModel](ABC):
    @abstractmethod
    def to_domain(self) -> DomainModel: ...

    @abstractmethod
    def to_read_model(self) -> ReadModel: ...

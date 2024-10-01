from enum import Enum


class SalesCustomerStatusName(str, Enum):
    INITIAL = "initial"
    CONVERTED = "converted"
    ARCHIVED = "archived"

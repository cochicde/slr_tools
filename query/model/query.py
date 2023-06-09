from enum import Enum


class Operator(Enum):
    AND = 1
    OR = 2


class Field(Enum):
    TITLE = 1
    ABSTRACT = 2
    KEYWORDS = 3
    ALL = 4


class SingleQuery:
    def __init__(
        self, operator: Operator, negated: bool, fields: list[Field], terms: list[str]
    ):
        self.operator = operator
        self.negated = negated
        self.fields = fields
        self.terms = terms


class Query:
    def __init__(self, operator: Operator, queries: list):
        self.operator = operator
        self.queries = queries

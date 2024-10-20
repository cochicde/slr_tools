from enum import Enum

class Operator(Enum):
    """ Available operators in the query
    """
    AND = 1
    OR = 2


class Field(Enum):
    """ Available fields to add to the query
    """
    TITLE = 1
    ABSTRACT = 2
    KEYWORDS = 3
    ALL = 4


class SingleQuery:
    """ Represents a single query part
    """
    def __init__(
        self, operator: Operator, negated: bool, fields: list[Field], terms: list[str]
    ):
        """ Constructor

        Args:
            operator (Operator): Operator to be applied to the given fields
            negated (bool): Is the query negated or not
            fields (list[Field]): List of fields where to look for the terms
            terms (list[str]): Terms to look for
        """
        self.operator = operator
        self.negated = negated
        self.fields = fields
        self.terms = terms


class Query:
    """ Representation of a list of single queries
    """
    def __init__(self, operator: Operator, queries: list[SingleQuery]) -> None:
        """ Constructor

        Args:
            operator (Operator): Operatot to apply to list of queries
            queries (list[SingleQuery]): List of queries
        """
        self.operator = operator
        self.queries = queries

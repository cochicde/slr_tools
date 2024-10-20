from enum import Enum

from query.model.query import Query, SingleQuery, Operator, Field

__OPERATOR_VALUE_MAP__ = {"and": Operator.AND, "or": Operator.OR}


def operator_from_string(operator: str) -> Operator:
    """ Get the operator from its string representation

    Args:
        operator (str): string representation of an operator

    Returns:
        Operator: Operator value 
    """
    return __OPERATOR_VALUE_MAP__.get(operator.lower(), None)


__FEILD_VALUE_MAP__ = {
    "title": Field.TITLE,
    "abstract": Field.ABSTRACT,
    "keywords": Field.KEYWORDS,
    "all": Field.ALL,
}


def field_from_string(field: str) -> Field:
    """ Get field from its string representation

    Args:
        field (str): string representation of a field

    Returns:
        Field: Field value
    """
    return __FEILD_VALUE_MAP__.get(field.lower(), None)


class SingleQueryKeys(Enum):
    """ Possible keys for a SingleQuery representation
    """
    NEGATED = 0
    OPERATOR = 1
    FIELDS = 2
    TERMS = 3


__SINGLE_QUERY_KEY_MAP__ = {
    SingleQueryKeys.NEGATED: "negated",
    SingleQueryKeys.OPERATOR: "operator",
    SingleQueryKeys.FIELDS: "fields",
    SingleQueryKeys.TERMS: "terms",
}

__SINGLE_QUERY_DEFAULT_OPERATOR__ = Operator.OR


def single_query_from_dict(query: dict) -> SingleQuery:
    """ Get a SingleQuery representation from a dictionary object

    Args:
        query (dict): Dictionary with the key/values of a single query

    Raises:
        Exception: If a negated field does not have a boolean type
        Exception: An unrecognized operator is found
        Exception: A fields or terms key is missing
        Exception: A field is unrecognized

    Returns:
        SingleQuery: Single query representation
    """
    fields = []
    terms = []

    ### Negated or not
    negated = query.get(__SINGLE_QUERY_KEY_MAP__[SingleQueryKeys.NEGATED], False)
    if type(negated) is not bool:
        raise Exception(
            "The negated field is not recognized. negated = "
            + __SINGLE_QUERY_KEY_MAP__[SingleQueryKeys.NEGATED]
            + "\nquery = "
            + str(query)
        )

    ### Operator
    operator_key = __SINGLE_QUERY_KEY_MAP__[SingleQueryKeys.OPERATOR]
    if operator_key in query:
        operator = operator_from_string(query.get(operator_key))

        if operator is None:
            raise Exception(
                "The operator is not recognized. operator = "
                + query.get(operator_key)
                + "\nquery = "
                + str(query)
            )
    else:
        operator = __SINGLE_QUERY_DEFAULT_OPERATOR__

    ### fields
    fields_key = __SINGLE_QUERY_KEY_MAP__[SingleQueryKeys.FIELDS]
    if fields_key not in query:
        raise Exception(
            "The '"
            + __SINGLE_QUERY_KEY_MAP__[SingleQueryKeys.FIELDS]
            + "' key is missing"
            + "\nquery = "
            + str(query)
        )

    for field in query[fields_key]:
        field_to_add = field_from_string(field)
        if field_to_add is None:
            raise Exception(
                "The field is unrecognized. field = "
                + str(field)
                + "\nquery = "
                + str(query)
            )

        fields.append(field_to_add)

    ### Terms
    terms_key = __SINGLE_QUERY_KEY_MAP__[SingleQueryKeys.TERMS]
    if terms_key not in query:
        raise Exception(
            "The '"
            + __SINGLE_QUERY_KEY_MAP__[SingleQueryKeys.TERMS]
            + "' key is missing"
            + "\nquery = "
            + str(query)
        )

    for term in query[terms_key]:
        terms.append(term)

    return SingleQuery(operator, negated, fields, terms)


class QueryKeys(Enum):
    """ Possible keys for a Query representation
    """
    QUERIES = 0
    OPERATOR = 1


__QUERY_KEY_MAP__ = {
    QueryKeys.QUERIES: "queries",
    QueryKeys.OPERATOR: "operator",
}

__QUERY_DEFAULT_OPERATOR__ = Operator.AND


def query_from_dict(query: dict) -> Query:
    """ Get a Query representation from a dictionary object

    Args:
        query (dict): Dictionary with the key/values of a single query

    Raises:
        Exception: An unrecognized operator is found

    Returns:
        Query: Query representation
    """
    queries = []

    operator_key = __QUERY_KEY_MAP__[QueryKeys.OPERATOR]
    if operator_key in query:
        operator = operator_from_string(query.get(operator_key))

        if operator is None:
            raise Exception(
                "The operator is not recognized. operator = "
                + query.get(operator_key)
                + "\nquery = "
                + str(query)
            )
    else:
        operator = __QUERY_DEFAULT_OPERATOR__

    queries_key = __QUERY_KEY_MAP__[QueryKeys.QUERIES]
    for inner_query in query[queries_key]:
        if queries_key in inner_query:
            queries.append(query_from_dict(inner_query))
        else:
            queries.append(single_query_from_dict(inner_query))

    return Query(operator, queries)

from query.model.query import Operator, Query, SingleQuery


class QueyGenerator:
    """ Abstract class for a query generator
    """
    def get_operator_string(operator: Operator) -> str:
        """ Get the string represenation of an operator

        Args:
            operator (Operator): required operator

        Returns:
            str: String representation of the operator
        """
        pass

    def get_single_query_string(query: SingleQuery) -> str:
        """ Get the string representation of a SingleQuery

        Args:
            query (SingleQuery): single query to get the representation from

        Returns:
            str: string representation of the single query
        """
        pass


def get_query_string(query: Query, generator: QueyGenerator) -> str:
    """ Gets the string representation of a query for the generator type 

    Args:
        query (Query): Query representation to be transformed into a string
        generator (QueyGenerator): Specific generator to be used

    Returns:
        str: String representation of the query based on the generator
    """
    to_return = ""
    only_one = len(query.queries) == 1

    for index, sub_query in enumerate(query.queries):
        if index != 0:
            to_return += " "
        if type(sub_query) == Query:
            to_return += "("
            to_return += get_query_string(sub_query, generator)
            to_return += ")"
        else:
            to_return += generator.get_single_query_string(sub_query)

        if not only_one and index != len(query.queries) - 1:
            to_return += " " + generator.get_operator_string(query.operator)

    return to_return

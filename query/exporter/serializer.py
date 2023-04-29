from query.model.query import Operator, Query, SingleQuery


class DatabaseQuery:
    def get_operator_string(operator: Operator):
        pass

    def get_single_query_string(query: SingleQuery):
        pass


def get_query_string(query: Query, database: DatabaseQuery):
    to_return = ""
    only_one = len(query.queries) == 1

    for index, sub_query in enumerate(query.queries):
        if index != 0:
            to_return += " "
        if type(sub_query) == Query:
            to_return += get_query_string(sub_query, database)
        else:
            to_return += database.get_single_query_string(sub_query)

        if not only_one and index != len(query.queries) - 1:
            to_return += " " + database.get_operator_string(query.operator)

    return to_return

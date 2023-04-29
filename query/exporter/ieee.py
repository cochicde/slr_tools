from query.model.query import Field, Operator, SingleQuery
from query.exporter.serializer import DatabaseQuery


class IEEEQuery(DatabaseQuery):
    __OPERATOR_MAP = {Operator.AND: "AND", Operator.OR: "OR"}
    __FIELDS_MAP = {
        Field.TITLE: '"Document Title"',
        Field.ABSTRACT: '"Abstract"',
        Field.KEYWORDS: '"Author Keywords"',
        Field.ALL: '"Full Text Only"',
    }

    def get_operator_string(operator: Operator):
        return IEEEQuery.__OPERATOR_MAP.get(operator)

    def get_single_query_string(query: SingleQuery):
        to_return = "("

        only_one_field = len(query.fields) == 1
        only_one_term = len(query.terms) == 1

        for index, field in enumerate(query.fields):
            if index != 0:
                to_return += " "

            if query.negated:
                to_return += "NOT ("

            for index_term, term in enumerate(query.terms):
                if index_term != 0:
                    to_return += " "

                to_return += IEEEQuery.__FIELDS_MAP[field] + ":"

                to_return += '"' + term + '"'
                if not only_one_term and index_term != len(query.terms) - 1:
                    to_return += " " + IEEEQuery.get_operator_string(query.operator)

            if query.negated:
                to_return += ")"

            if not only_one_field and index != len(query.fields) - 1:
                to_return += " " + IEEEQuery.get_operator_string(query.operator)

        to_return += ")"

        return to_return

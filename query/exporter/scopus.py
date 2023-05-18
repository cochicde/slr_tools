from query.model.query import Field, Operator, SingleQuery
from query.exporter.serializer import DatabaseQuery


class ScopusQuery(DatabaseQuery):
    __OPERATOR_MAP = {Operator.AND: "AND", Operator.OR: "OR"}
    __FIELDS_MAP = {
        Field.TITLE: "TITLE",
        Field.ABSTRACT: "ABSTRACT",
        Field.KEYWORDS: "KEYWORDS",
        Field.ALL: "ALL",
        "TITLE-ABS-KEY": "TITLE-ABS-KEY",
    }

    def get_operator_string(operator: Operator):
        return ScopusQuery.__OPERATOR_MAP.get(operator)

    def get_single_query_string(query: SingleQuery):
        to_return = ""

        fields = query.fields.copy()

        if (
            Field.TITLE in fields
            and Field.ABSTRACT in fields
            and Field.KEYWORDS in fields
            and query.operator is Operator.OR
        ):
            fields.remove(Field.TITLE)
            fields.remove(Field.ABSTRACT)
            fields.remove(Field.KEYWORDS)
            fields.append("TITLE-ABS-KEY")

        only_one_field = len(fields) == 1

        if not only_one_field:
            to_return += "("

        only_one_term = len(query.terms) == 1

        for index, field in enumerate(fields):
            if index != 0:
                to_return += " "

            if query.negated:
                to_return += "NOT "

            to_return += ScopusQuery.__FIELDS_MAP[field] + "("

            for index_term, term in enumerate(query.terms):
                if index_term != 0:
                    to_return += " "

                to_return += '"' + term + '"'
                if not only_one_term and index_term != len(query.terms) - 1:
                    to_return += " " + ScopusQuery.get_operator_string(query.operator)

            to_return += ")"

            if not only_one_field and index != len(fields) - 1:
                to_return += ScopusQuery.get_operator_string(query.operator)

        if not only_one_field:
            to_return += ")"

        return to_return

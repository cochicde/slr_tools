import argparse
from query.controller.yaml import query_from_yaml
from query.exporter.serializer import get_query_string
from query.exporter.scopus import ScopusQuery
from query.exporter.ieee import IEEEQuery
from query.exporter.acm import ACMQuery
from database.remote.scopus import ScopusDatabase
from parameters.provider import Provider


def main():
    parser = argparse.ArgumentParser(prog="Query Generator")

    parser.add_argument(
        "-f", "--file", help="File with the query source words", default="./query.yml"
    )

    parser.add_argument(
        "-p",
        "--parameter",
        help="Paramter to one of the conectors in the form CONNECTOR_NAME.PARAMETER",
        action="append",
    )

    args = parser.parse_args()

    # initilize global parameter provider
    Provider.initialize(args.parameter)

    query = query_from_yaml(args.file)

    scopus = ScopusDatabase()
    resources = scopus.request(query)

    for resource in resources:
        print(
            "doi:"
            + resource.doi
            + ", title:"
            + resource.title
            + ", abstract:"
            + resource.abstract
            + ", link: "
            + resource.link
            + ", issn: "
            + resource.issn
            + ", isbn: "
            + resource.isbn
        )


if __name__ == "__main__":
    main()

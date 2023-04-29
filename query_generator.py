import argparse
from query.controller.yaml import query_from_yaml
from query.exporter.serializer import get_query_string
from query.exporter.scopus import ScopusQuery
from query.exporter.ieee import IEEEQuery
from query.exporter.acm import ACMQuery


def main():
    parser = argparse.ArgumentParser(prog="Query Generator")

    parser.add_argument(
        "-f", "--file", help="File with the query source words", default="./query.yml"
    )

    args = parser.parse_args()

    query = query_from_yaml(args.file)

    print(get_query_string(query, IEEEQuery))
    print("")
    print(get_query_string(query, ACMQuery))
    print("")
    print(get_query_string(query, ScopusQuery))


if __name__ == "__main__":
    main()

import argparse
from query.controller.yaml import query_from_yaml
from query.exporter.serializer import get_query_string
from query.exporter.scopus import ScopusQuery
from query.exporter.ieee import IEEEQuery
from query.exporter.acm import ACMQuery


def print_title(title: str, char: str = "=") -> None:
    border = char * (len(title) + 6)
    print(border)
    print(char * 2 + " " + title + " " + char * 2)
    print(border)


def main():
    parser = argparse.ArgumentParser(prog="Query Generator")

    parser.add_argument(
        "-q",
        "--query-file",
        help="File with the query source words",
        default="./query.yml",
    )

    args = parser.parse_args()

    query = query_from_yaml(args.query_file)

    print_title("SCOPUS")
    print(get_query_string(query, ScopusQuery))

    print_title("IEEE")
    print(get_query_string(query, IEEEQuery))

    print_title("ACM")
    print(get_query_string(query, ACMQuery))


if __name__ == "__main__":
    main()

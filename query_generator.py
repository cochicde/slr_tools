import argparse
from query.controller.yaml import query_from_yaml
from query.exporter.serializer import get_query_string
from query.exporter.scopus import ScopusQuery
from query.exporter.ieee import IEEEQuery
from query.exporter.acm import ACMQuery
from database.remote.scopus import ScopusDatabase
from parameters.provider import Provider
from database.local.sqlite import Sqlite3
from gui.application import ApplicationGUI
from database.local.columns import Columns


def main():
    parser = argparse.ArgumentParser(prog="Query Generator")

    parser.add_argument(
        "-q",
        "--query-file",
        help="File with the query source words",
        default="./query.yml",
    )

    parser.add_argument(
        "-p",
        "--parameter",
        help="Paramter to one of the modules in the form MODULE.PARAMETER=VALUE",
        action="append",
    )

    parser.add_argument(
        "-d",
        "--database",
        help="Database where to store results",
        default="test.db",
    )

    # from literature.data import ResourceData

    # resource = ResourceData(
    #     "myDoi",
    #     "myISBN",
    #     "myTitle",
    #     "myAbstractdddsdfasdfsdaflshdfgkdjsghdklf;jgfdflknvdfjklnvlkdfsjvndl;fsjvndsl;kvndk;fljvbdjkfslvndfjklvnklds",
    #     "myKeywords",
    # )

    args = parser.parse_args()

    # initilize global parameter provider
    Provider.initialize(args.parameter)

    app = ApplicationGUI(args.database)
    app.launch()
    return

    query = query_from_yaml(args.query_file)

    # scopus = ScopusDatabase(query)
    # database = Sqlite3(args.database)
    # resources = scopus.request_first()
    # database.store(resources, "scopus")

    entries = database.get_not_reviewed()
    for entry in entries:
        (id, Entry) = entry

        print("ID: " + str(id) + " Entry:" + Entry.print())


if __name__ == "__main__":
    main()

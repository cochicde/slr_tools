import argparse
from query.controller.yaml import query_from_yaml
from database.remote.scopus import ScopusDatabase
from parameters.provider import Provider
from database.local.sqlite import Sqlite3
import yaml


def main():
    parser = argparse.ArgumentParser(prog="Query Remote Databases")

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

    parser.add_argument(
        "-c",
        "--config",
        help="Configuration yaml file",
    )

    args = parser.parse_args()

    if args.config is not None:
        with open(args.config) as config:
            yaml_config = yaml.load(config, Loader=yaml.FullLoader)

            class Object(object):
                pass

            args = Object()
            for key, value in yaml_config["config"].items():
                if key == "parameter":
                    values = []

                    for provider_name, provider_value in value.items():
                        for argument_name, argument_value in provider_value.items():
                            values.append(
                                provider_name
                                + "."
                                + argument_name
                                + "="
                                + str(argument_value)
                            )

                    args.__setattr__(key, values)
                    continue

                args.__setattr__(key, value)

    # initilize global parameter provider
    Provider.initialize(args.parameter)

    query = query_from_yaml(args.query_file)

    scopus = ScopusDatabase(query)
    database = Sqlite3(args.database)
    resources = scopus.request_first()

    while len(resources) != 0:
        database.insert(resources)
        resources = scopus.request_next()


if __name__ == "__main__":
    main()

from command.command_base import CommandBase
from database.connector import Connector
from loader.file import ieee_csv
from loader.file import bibtex
from loader.remote.parameters import Parameters
from query.importer.yaml import query_from_yaml
from loader.remote.scopus import Scopus
from loader.remote.ieee import IEEE

class Loader(CommandBase):
  """ Loads scientific resources into a local database
  """

  NAME = "load"

  def __init__(self, args) -> None:
      super().__init__(args)

  @staticmethod
  def add_parameters(subparsers):
      """ Add needed arguments for the loader command. It includes:
        - a database
        - bibtex file
        - ieee csv file
        - remote connection configuration
        - enable remote connection to ieee
        - enable remote connection to scopus

      Args:
          subparsers: Subparsers where to add the arguments to
      """
      parser = subparsers.add_parser(Loader.NAME, description='loads scientific resources into a local database')

      parser.add_argument(
        "-d",
        "--database",
        required=True,
        help="Database where to store results",
        default="./example/test.db",
      )

      parser.add_argument(
        "-b",
        "--bibtex",
        action="append",
        help="bibtex file to import from.",
      )

      parser.add_argument(
        "-c",
        "--csv",
        action="append",
        help="IEEE Csv file to import from.",
      )

      parser.add_argument(
        "--remote-ieee",
        action="store_true",
        help="Get resources from ieee remotely. This functionality is deprecated and not maintained anymore",
      )

      parser.add_argument(
        "--remote-scopus",
        action="store_true",
        help="Get resources from scopus remotely. This functionality is deprecated and not maintained anymore",
      )

      parser.add_argument(
        "--config",
        help="Configuration yaml file for remote loading. This functionality is deprecated and not maintained anymore",
      )

  def execute(self):
      """ Execute the loader command
      """
      database = Connector.get_database(self.args.database)

      if self.args.csv is not None:
          for file in self.args.csv:
              resources = ieee_csv.get_entries(file)
              database.insert(resources)

      if self.args.bibtex is not None:
          for file in self.args.bibtex:
              resources = bibtex.get_entries(file)
              database.insert(resources)

      if self.args.config is not None:
          Parameters.initialize(self.args.config)

      if Parameters.GLOBAL_PARAMETERS.get("query_file") is None:
          return

      query = query_from_yaml(Parameters.GLOBAL_PARAMETERS["query_file"])

      if self.args.remote_ieee:
          ieee = IEEE(query)
          resources = ieee.request_all()
          database.insert(resources)

      if self.args.remote_scopus:
          scopus = Scopus(query)
          resources = scopus.request_all()
          database.insert(resources)



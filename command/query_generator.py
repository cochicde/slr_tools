from command.command_base import CommandBase

from query.importer.yaml import query_from_yaml
from query.exporter.serializer import get_query_string
from query.exporter.scopus import ScopusQuery
from query.exporter.ieee import IEEEQuery
from query.exporter.acm import ACMQuery


class QueryGenerator(CommandBase):
  """ Generate queries for different pages according to a query file
  """

  NAME = "query"

  def __init__(self, args) -> None:
      super().__init__(args)

  @staticmethod
  def add_parameters(subparsers):
      """ Add needed arguments for the query generator command. It includes:
        - a query file

      Args:
          subparsers: Subparsers where to add the arguments to
      """
      parser = subparsers.add_parser(QueryGenerator.NAME, description='generate query for different pages')

      parser.add_argument(
          "-q",
          "--query-file",
          help="File with the query source words",
          default="./example/query.yml",
      )

  def execute(self):
      """ Execute the query generator command
      """
      query = query_from_yaml(self.args.query_file)

      self.__print_title("SCOPUS")
      print(get_query_string(query, ScopusQuery))

      self.__print_title("IEEE")
      print(get_query_string(query, IEEEQuery))

      self.__print_title("ACM")
      print(get_query_string(query, ACMQuery))

  def __print_title(self, title: str, char: str = "=") -> None:
      border = char * (len(title) + 6)
      print(border)
      print(char * 2 + " " + title + " " + char * 2)
      print(border)


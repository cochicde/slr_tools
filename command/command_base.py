import argparse

from typing import Self

class CommandBase:
  """ Base class for all commands
  """

  NAME = ""

  def __init__(self, args: argparse.Namespace) -> None:
      """ Constructor. Stores the arguments

      Args:
          args (argparse.Namespace): Arguments to the command
      """
      self.args = args
  
  @staticmethod
  def add_parameters(subparsers) -> None:
      """ Add needed parameters for the command to properly execute

      Args:
          subparsers: Subparser where to add the arguments
      """
      pass
  
  def execute() -> None:
      """ Execute the command
      """
      pass

  @staticmethod            
  def load_commands(subparsers):
      """ Load commands and their arguments

      Args:
          subparsers: Subparser where to add the arguments
      """
      for command in CommandBase.__subclasses__():
         command.add_parameters(subparsers)

  @staticmethod            
  def get_command_instance(class_name: str, args: argparse.Namespace) -> Self | None:
      """ Searches the comand that inherits from CommandBase and matches the command name

      Args:
          class_name (str): Name of the command to look for
          args (argparse.Namespace): Arguments to pass to the command

      Returns:
          Self | None: A command instance if the name exist, None otherwise
      """
      name_and_classes = {cls.NAME : cls for cls in CommandBase.__subclasses__()}
      command_class = name_and_classes.get(class_name)
      if command_class is not None:
          return command_class(args)
      
      return None
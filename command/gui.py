import yaml

from command.command_base import CommandBase
from gui.application import ApplicationGUI



class GUI(CommandBase):
  """ Start the GUI
  """

  NAME = "gui"

  def __init__(self, args) -> None:
      super().__init__(args)

  @staticmethod
  def add_parameters(subparsers):
      """ Add needed arguments for the GUI command. It includes:
        - a config file

      Args:
          subparsers: Subparsers where to add the arguments to
      """
      parser = subparsers.add_parser(GUI.NAME, description='run GUI for a database')

      parser.add_argument(
        "-c", 
        "--config", 
        help="Configuration yaml file", 
        default="./example/config-gui.yml"
    )

  def execute(self):
      """ Execute the gui command
      """
      with open(self.args.config) as config:
        args = yaml.load(config, Loader=yaml.FullLoader)
        app = ApplicationGUI(args["config"])
        app.launch()

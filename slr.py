import argparse

from command.command_base import CommandBase 

def main():
  parser = argparse.ArgumentParser(prog='slr')

  subparsers = parser.add_subparsers(dest="slr")

  CommandBase.load_commands(subparsers)

  args = parser.parse_args()

  command = CommandBase.get_command_instance(args.slr, args)
  command.execute()


if __name__ == "__main__":
  main()


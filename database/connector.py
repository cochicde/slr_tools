from typing import Self

from database.entry import Entry


class Connector:
    """ Abstract class with all capabilities needed to handle the database. Connections to specific 
    databases should inherit from this.
    """

    def __init__(self, database: str) -> None:
        """ Constructor

        Args:
            database (str): Path to the database
        """
        pass

    def insert(self, entries: list[Entry]) -> None:
        """ Insert entries to the database

        Args:
            entries (list[Entry]): List of entries to inseret into the database
        """
        pass

    def get_entries(self, rejected: [int]) -> list[(int, Entry)]:
        """ Get all entries with the given rejected values
        """
        pass

    def update_rejected(self, id: int, reason: int, save: bool = False) -> None:
        """ Update the rejected field of an entry

        Args:
            id (int): ID of the entry to update
            reason (int): reason for rejection
            save (bool, optional): Save into the database now or no. Defaults to False. Since writing to the database
            can be slow, the information can be save in memory and only later saved
        """
        pass

    def update_save_for_later(self, id: int, save_for_later: bool, save: bool = False) -> None:
        """ Update the save for later field

        Args:
            id (int): ID of the entry to update
            save_for_later (bool): new value for the field of the entry
            save (bool, optional): Save into the database now or no. Defaults to False. Since writing to the database
            can be slow, the information can be save in memory and only later saved
        """
        pass

    def update_notes(self, id: int, notes: bool, save: bool = False) -> None:
        """ Update the note field

        Args:
            id (int): ID of the entry to update
            notes (bool): new description for the notes field of the entry
            save (bool, optional): Save into the database now or no. Defaults to False. Since writing to the database
            can be slow, the information can be save in memory and only later saved
        """
        pass

    def save(self) -> None:
        """ Save current state of the database into its file
        """
        pass

    @staticmethod
    def get_database(args) -> Self | None:
      """ Gets the database from the passed arguments. For now, only sqlite3 is supported

      Args:

      Returns:
          Self | None: A connector to a database, None if the arguments passed do point to an non-existing type
      """
      classes = Connector.__subclasses__()
      return classes[0](args)
          

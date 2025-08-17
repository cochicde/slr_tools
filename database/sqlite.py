import sqlite3

from database.columns import Columns
from database.connector import Connector
from database.entry import Entry, EntrySource, EntryState
from model.resource import ResourceData

class Sqlite3(Connector):
    """ Conector to a Sqlite3 database. The connector creates a "main" table with all the information about an entry
    except the sources. The sources are stored in their own table with the ID as link to the main table.
    """

    __MAIN_TABLE_NAME = "main"

    def __init__(self, database: str) -> None:
        """ Constructor. Connects to the database and creates the main table if not present

        Args:
            database (str):Path to the database
        """
        self.connection = sqlite3.connect(database)
        cursor = self.connection.cursor()

        # Create the main table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            + Sqlite3.__MAIN_TABLE_NAME
            + "(id INTEGER PRIMARY KEY, doi TEXT(255), isbn TEXT(25), title TEXT(255), abstract TEXT, keywords TEXT, rejected TINYINT, later BOOL, notes TEXT)"
        )

        self.connection.commit()

        # Get existing table names
        self.tables = [
            table_tuple[0]
            for table_tuple in cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        self.tables.remove(Sqlite3.__MAIN_TABLE_NAME)

    def __entry_factory(cursor: sqlite3.Cursor, row: tuple[any,...]) -> tuple[int, Entry]:
        """ Row factory for sqlite3. When fetching from the database, this function transform the default return from the database (tuple of colums)
        into a custom made row. 

        Args:
            cursor (sqlite3.Cursor): Cursor executing the command
            row (tuple[any,...]): Row being fetched

        Returns:
            tuple[int, Entry]: ID and Entry object created from the fetch row
        """
        
        sources = []
        # sources, if present in the fetch command, should be located after the rest of the information
        for column in range(Columns.UNKNOWN, len(cursor.description)):
            if row[column] is not None:
                sources.append(EntrySource(cursor.description[column][0], row[column]))

        return (
            row[Columns.ID],
            Entry(
                ResourceData(
                    row[Columns.DOI],
                    row[Columns.ISBN],
                    row[Columns.TITLE],
                    row[Columns.ABSTRACT],
                    row[Columns.KEYWORDS],
                ),
                sources,
                EntryState(
                    row[Columns.REJECTED],
                    bool(row[Columns.SAVE_FOR_LATER]),
                    row[Columns.NOTES],
                ),
            ),
        )

    def insert(self, entries: list[Entry]) -> None:
        """ Insert entries into the database

        Args:
            entries (list[Entry]): Entries to insert into the database
        """
        cursor = self.connection.cursor()
        new_entries = 0
        for entry in entries:
            # add source tables if they do not exist
            for source in entry.sources:
                if source.origin not in self.tables:
                    cursor.execute(
                        "CREATE TABLE IF NOT EXISTS "
                        + source.origin
                        + " (id INT UNSIGNED, link TEXT)"
                    )
                    self.tables.append(source.origin)

            data = (
                None,
                entry.resource.doi,
                entry.resource.isbn,
                entry.resource.title,
                entry.resource.abstract,
                entry.resource.keywords,
                entry.state.rejected,
                entry.state.save_for_later,
                entry.state.notes,
            )

            # insert into the main table only if not present already
            existing_row = self.get_existing_row(entry, cursor) 
            if existing_row is None:
                cursor.execute(
                    "INSERT INTO "
                    + Sqlite3.__MAIN_TABLE_NAME
                    + " ('id', 'doi', 'isbn', 'title', 'abstract', 'keywords', 'rejected', 'later', 'notes') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    data,
                )
                new_entries = new_entries + 1

            # insert the information into the source table
            id_to_insert = existing_row[0] if existing_row is not None else cursor.lastrowid
            for source in entry.sources:
                cursor.execute(
                    "INSERT INTO " + source.origin + " VALUES (?, ?)",
                    (id_to_insert, source.link),
                )

        self.connection.commit()

        print(entries[0].sources[0].origin + " -> " + str(new_entries))

    def get_existing_row(self, entry: Entry, cursor: sqlite3.Cursor) -> tuple[int, Entry] | None:
        """ Get a row based on an Entry if it exist. A row is considered to exists if it has one of the following values equal to another in the database:
          doi, title, abstract. ISBN is not used since sometime scientific resources are in the same book having the same ISBN.
        If many items exists in the database that are equal, the first one is returned. 

        Args:
            entry (Entry): Entry to look for in the database
            cursor (sqlite3.Cursor): Cursor of the database

        Returns:
            tuple[int, Entry] | None: The ID and entry if the Entry was already present, None otherwise.
        """
        cursor.row_factory = Sqlite3.__entry_factory

        fields_to_check = []
        if entry.resource.doi != '':
            fields_to_check.append(' doi = "' + entry.resource.doi.replace('"', '""')  + '"')
        if entry.resource.title != '':
            fields_to_check.append(' title = "' + entry.resource.title.replace('"', '""')  + '"')
        if entry.resource.abstract != '':
            fields_to_check.append(' abstract = "' + entry.resource.abstract.replace('"', '""')  + '"')

        command = (  'SELECT * ' +
                    ' FROM ' + Sqlite3.__MAIN_TABLE_NAME +
                    ' WHERE' +
                    " OR ".join(fields_to_check) +
                    ' COLLATE NOCASE')
        existing_entries = cursor.execute(command).fetchall()
        if len(existing_entries) != 0:
            # return first row found
            return existing_entries[0]
        
        return None

    def get_entries(self, rejected: [int]) -> list[tuple[int, Entry]]:
        """ Get all entries that are not reviewed yet (rejected = 0)
    
        Returns:
          list[tuple[int, Entry]]: List of ID and entries which are not reviwied yet
        """
        cursor = self.connection.cursor()
        cursor.row_factory = Sqlite3.__entry_factory

        links_columns = ""
        links_inner_joins = ""
        for table in self.tables:
            links_columns += ", " + table + ".link AS " + table
            links_inner_joins += " LEFT JOIN " + table + " ON main.id=" + table + ".id"

        return cursor.execute(
            "SELECT main.id, main.doi, main.isbn, main.title, main.abstract, main.keywords, main.rejected, main.later, main.notes"
            + links_columns
            + " FROM "
            + Sqlite3.__MAIN_TABLE_NAME
            + links_inner_joins
            + " WHERE rejected IN (" + ", ".join(str(r) for r in rejected) + ")"
        ).fetchall()

    def __update_field(self, id: int, field: str, value: str, save: bool = False):
        cursor = self.connection.cursor()

        cursor.execute(
            "UPDATE "
            + Sqlite3.__MAIN_TABLE_NAME
            + " SET "
            + field
            + "="
            + value
            + " WHERE id="
            + str(id)
        )

        if save:
            self.connection.commit()

    def update_rejected(self, id: int, reason: int, save: bool = False):
        """ Update the rejected field of an entry

        Args:
            id (int): ID of the entry to update
            reason (int): reason for rejection
            save (bool, optional): Save into the database now or no. Defaults to False. Since writing to the database
            can be slow, the information can be save in memory and only later saved
        """
        self.__update_field(id, "rejected", str(reason), save)

    def update_save_for_later(self, id: int, save_for_later: bool, save: bool = False):
        """ Update the save for later field

        Args:
            id (int): ID of the entry to update
            save_for_later (bool): new value for the field of the entry
            save (bool, optional): Save into the database now or no. Defaults to False. Since writing to the database
            can be slow, the information can be save in memory and only later saved
        """
        self.__update_field(id, "later", str(save_for_later).upper(), save)

    def update_notes(self, id: int, notes: bool, save: bool = False):
        """ Update the note field

        Args:
            id (int): ID of the entry to update
            notes (bool): new description for the notes field of the entry
            save (bool, optional): Save into the database now or no. Defaults to False. Since writing to the database
            can be slow, the information can be save in memory and only later saved
        """
        self.__update_field(id, "notes", "'" + notes.replace("'", "''") + "'", save)

    def save(self):
        """ Save current state of the database into its file
        """
        self.connection.commit()

import sqlite3

from database.local.connector import Connector

from database.entry import Entry, EntrySource, EntryState
from literature.data import ResourceData
from database.local.columns import Columns


class Sqlite3(Connector):
    __MAIN_TABLE_NAME = "main"

    def __init__(self, database: str) -> None:
        self.connection = sqlite3.connect(database)
        cursor = self.connection.cursor()

        # Create the main table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            + Sqlite3.__MAIN_TABLE_NAME
            + "(id INTEGER PRIMARY KEY, doi TEXT(255), isbn TEXT(25), title TEXT(255), abstract TEXT, keywords TEXT, rejected TINYINT, later BOOL)"
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

    def __entry_factory(cursor, row):
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
                [
                    EntrySource(cursor.description[x][0], row[x])
                    for x in range(Columns.KEYWORDS + 3, len(cursor.description))
                ],
                EntryState(row[Columns.REJECTED], bool(row[Columns.SAVE_FOR_LATER])),
            ),
        )

    def insert(self, entries: list[Entry]) -> None:
        cursor = self.connection.cursor()
        for entry in entries:
            # add source tables if does not exist
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
            )
            cursor.execute(
                "INSERT INTO "
                + Sqlite3.__MAIN_TABLE_NAME
                + " ('id', 'doi', 'isbn', 'title', 'abstract', 'keywords', 'rejected', 'later') VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                data,
            )

            for source in entry.sources:
                cursor.execute(
                    "INSERT INTO " + source.origin + " VALUES (?, ?)",
                    (cursor.lastrowid, source.link),
                )

        self.connection.commit()

    def get_not_reviewed(self) -> list[(int, Entry)]:
        cursor = self.connection.cursor()
        cursor.row_factory = Sqlite3.__entry_factory

        links_columns = ""
        links_inner_joins = ""
        for table in self.tables:
            links_columns += ", " + table + ".link AS " + table
            links_inner_joins += " LEFT JOIN " + table + " ON main.id=" + table + ".id"

        return cursor.execute(
            "SELECT main.id, main.doi, main.isbn, main.title, main.abstract, main.keywords, main.rejected, main.later"
            + links_columns
            + " FROM "
            + Sqlite3.__MAIN_TABLE_NAME
            + links_inner_joins
            + " WHERE rejected is 0"
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
        self.__update_field(id, "rejected", str(reason), save)

    def update_save_for_later(self, id: int, save_for_later: bool, save: bool = False):
        self.__update_field(id, "later", str(save_for_later).upper(), save)

    def save(self):
        self.connection.commit()

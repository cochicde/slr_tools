import sqlite3

from database.local.connector import Connector

from database.entry import Entry


class Sqlite3(Connector):
    def __init__(self, database: str) -> None:
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS main(id INTEGER PRIMARY KEY, doi TEXT(255), isbn TEXT(25), title TEXT(255), abstract TEXT, keywords TEXT, rejected TINYINT, later BOOL)"
        )
        self.connection.commit()

    def store(self, entries: list[Entry], remote_database_name: str) -> None:
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            + remote_database_name
            + " (main_id INT UNSIGNED, link TEXT)"
        )

        for entry in entries:
            data = (
                None,
                entry.resource.doi,
                entry.resource.isbn,
                entry.resource.title,
                entry.resource.abstract,
                entry.resource.keywords,
                None,
                None,
            )
            self.cursor.execute(
                "INSERT INTO main ('id', 'doi', 'isbn', 'title', 'abstract', 'keywords', 'rejected', 'later') VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                data,
            )

            self.cursor.execute(
                "INSERT INTO " + remote_database_name + " VALUES (?, ?)",
                (self.cursor.lastrowid, entry.link),
            )

        self.connection.commit()

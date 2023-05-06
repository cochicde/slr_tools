import sqlite3

from database.local.connector import Connector

from database.entry import Entry


class Sqlite3(Connector):
    def __init__(self, database: str) -> None:
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS main(doi TEXT(255), isbn TEXT(25), title TEXT(255), abstract TEXT, link TEXT, rejected TINYINT, later BOOL)"
        )
        self.connection.commit()

    def store(self, entries: list[Entry]) -> None:
        for entry in entries:
            data = (
                entry.resource.doi,
                entry.resource.isbn,
                entry.resource.title,
                entry.resource.abstract,
                entry.link,
                0,
                False,
            )
            self.cursor.execute(
                "INSERT INTO main VALUES (?, ?, ?, ?, ?, ?, ?)",
                data,
            )

        self.connection.commit()

from database.entry import Entry


class Connector:
    def __init__(self, query: str) -> None:
        pass

    def request(self, query: str) -> list[Entry]:
        pass

    def next(self) -> list[Entry]:
        pass

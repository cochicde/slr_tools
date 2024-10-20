from database.entry import Entry


class Connector:
    def __init__(self, query: str) -> None:
        pass

    def request_all(self) -> list[Entry]:
        to_return = self.request_first()
        while True:
            prev_len = len(to_return)
            to_return.extend(self.request_next())
            if len(to_return) == prev_len:
                break

        return to_return

    def request_first(self) -> list[Entry]:
        pass

    def request_next(self) -> list[Entry]:
        pass

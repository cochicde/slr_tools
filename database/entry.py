from literature.data import ResourceData


class EntryState:
    def __init__(
        self, rejected: int = 0, save_for_later: bool = False, notes: str = ""
    ) -> None:
        self.rejected = rejected
        self.save_for_later = save_for_later
        self.notes = notes


class EntrySource:
    def __init__(self, origin: str, link: str) -> None:
        self.origin = origin
        self.link = link


class Entry:
    def __init__(
        self,
        resource: ResourceData,
        sources: list[EntrySource],
        state: EntryState = EntryState(),
    ):
        self.resource = resource
        self.sources = sources
        self.state = state

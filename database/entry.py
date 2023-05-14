from literature.data import ResourceData


class EntryState:
    def __init__(self, rejected: int = None, save_for_later: bool = False) -> None:
        self.rejected = rejected
        self.save_for_later = save_for_later


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

    def print(self):
        return (
            " DOI: "
            + self.resource.doi
            + " ISBN: "
            + self.resource.isbn
            + " Title: "
            + self.resource.title
            + " ABSTRACT: "
            + self.resource.abstract
            + " KEYRWORDS: "
            + self.resource.keywords
            + str(
                [
                    "Origin: "
                    + self.sources[x].origin
                    + " Link: "
                    + str(self.sources[x].link)
                    for x in range(len(self.sources))
                ]
            )
        )

from literature.data import ResourceData


class EntrySource:
    def __init__(self, origin: str, link: str) -> None:
        self.origin = origin
        self.link = link


class Entry:
    def __init__(self, resource: ResourceData, sources: list[EntrySource]):
        self.resource = resource
        self.sources = sources

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

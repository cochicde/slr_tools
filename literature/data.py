from enum import Enum


class ResourceFields(Enum):
    DOI = 1
    TITLE = 2
    ABSTRACT = 3
    LINK = 4
    ISSN = 5
    ISBN = 6


class ResourceData:
    def __init__(
        self, doi: str, title: str, abstract: str, link: str, issn: str, isbn: str
    ):
        self.doi = doi
        self.title = title
        self.abstract = abstract
        self.link = link
        self.issn = issn
        self.isbn = isbn

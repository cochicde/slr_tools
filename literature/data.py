from enum import Enum


class ResourceFields(Enum):
    DOI = 1
    ISBN = 2
    TITLE = 3
    ABSTRACT = 4
    KEYWORDS = 5


class ResourceData:
    def __init__(self, doi: str, isbn: str, title: str, abstract: str, keywords: str):
        self.doi = doi
        self.isbn = isbn
        self.title = title
        self.abstract = abstract
        self.keywords = keywords

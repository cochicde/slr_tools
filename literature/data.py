from enum import Enum


class ResourceFields(Enum):
    DOI = 0
    ISBN = 1
    TITLE = 2
    ABSTRACT = 3
    KEYWORDS = 4


class ResourceData:
    def __init__(self, doi: str, isbn: str, title: str, abstract: str, keywords: str):
        self.doi = doi
        self.isbn = isbn
        self.title = title
        self.abstract = abstract
        self.keywords = keywords
    
    def __str__(self) -> str:
        return ("Doi: " + self.doi + 
                "\nisbn: " + self.isbn +
                "\ntitle: " + self.title +
                "\nabstract: " + self.abstract +
                "\nkeywords: " + self.keywords
                )
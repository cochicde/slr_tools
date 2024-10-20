    
""" Contains all the information about a scientific resources
"""


from enum import Enum


class ResourceFields(Enum):
    """ Enumeration of the supported fields in a scientific resource 
    """
    DOI = 0
    ISBN = 1
    TITLE = 2
    ABSTRACT = 3
    KEYWORDS = 4


class ResourceData:
    """ Representation of a scientitic resource

    This class contains all the information supported
    """

    def __init__(self, doi: str, isbn: str, title: str, abstract: str, keywords: str):
        """ Constructor. An empty string shall be used for not present fields

        Args:
            doi (str): doi link
            isbn (str): ISBN nummber
            title (str): Title of the scientific resource
            abstract (str): Abstract of the scientific resource
            keywords (str): Keywords associated with the scientific resource, separated by ' | '
        """
        self.doi = doi
        self.isbn = isbn
        self.title = title
        self.abstract = abstract
        self.keywords = keywords
    
    def __str__(self) -> str:
        """ Get the string representaiton of a scientific resource. Useful for debugging purposses

        Returns:
            str: String represetantion of a scientific resource
        """
        return ("Doi: " + self.doi + 
                "\nisbn: " + self.isbn +
                "\ntitle: " + self.title +
                "\nabstract: " + self.abstract +
                "\nkeywords: " + self.keywords
                )
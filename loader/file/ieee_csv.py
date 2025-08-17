from enum import IntEnum
import csv
import os

from database.entry import Entry, EntrySource
from model.resource import ResourceData

class Headers(IntEnum):
    """ Available columns/headers in the IEEE csv file
    """
    DOCUMENT_TITLE = 0
    AUTHORS = 1
    AUTHOR_AFFILIATIONS = 2
    PUBLICATION_TITLE = 3
    DATE_ADDED_TO_XPLORE = 4
    PUBLICATION_YEAR = 5
    VOLUME = 6
    ISSUE = 7
    START_PAGE = 8
    END_PAGE = 9
    ABSTRACT = 10
    ISSN = 11
    ISBNS = 12
    DOI = 13
    FUNDING_INFORMATION = 14
    PDF_LINK = 15
    AUTHOR_KEYWORDS = 16
    IEEE_TERMS = 17
    MESH_TERMS = 18
    ARTICLE_CITATION_COUNT = 19
    PATENT_CITATION_COUNT = 20
    REFERENCE_COUNT = 21
    LICENSE = 22
    ONLINE_DATE = 23
    ISSUE_DATE = 24
    MEETING_DATE = 25
    PUBLISHER = 26
    DOCUMENT_IDENTIFIER = 27

def get_entries(source_file: str) -> list[Entry]:
    """ Gets a list of entry objects from a ieee csv file

    Args:
        source_file (str): Path to the ieee csv file

    Returns:
        list[Entry]: List of entries
    """
    result = []
    with open(source_file) as file:
        csv_input = csv.reader(file, delimiter=',', quoting=csv.QUOTE_ALL)
        source_file_no_ext = os.path.splitext(os.path.basename(source_file))[0]
        for line in csv_input:
            result.append(
                    Entry(
                        ResourceData(line[Headers.DOI], line[Headers.ISBNS], line[Headers.DOCUMENT_TITLE], line[Headers.ABSTRACT], line[Headers.AUTHOR_KEYWORDS].replace(";", " | ")),
                        [EntrySource(source_file_no_ext, line[Headers.PDF_LINK])],
                    )
                )

    return result[1:]
from enum import StrEnum
from pybtex.database import parse_file

from database.entry import Entry, EntrySource
from model.resource import ResourceData

import os

class Fields(StrEnum):
    """ Available fields in a bibtex entry
    """

    ABSTRACT  = "abstract"
    ADDRESS  = "address"
    ANNOTE  = "annote"
    AUTHOR  = "author"
    BOOKTITLE  = "booktitle"
    CHAPTER  = "chapter"
    CROSSREF  = "crossref"
    DOI = "doi"
    EDITION  = "edition"
    EDITOR  = "editor"
    HOWPUBLISHED  = "howpublished"
    INSTITUTION  = "institution"
    ISBN = "isbn"
    JOURNAL  = "journal"
    KEY  = "key"
    KEYWORDS = "keywords"
    MONTH  = "month"
    NOTE  = "note"
    NUMBER  = "number"
    ORGANIZATION  = "organization"
    PAGES  = "pages"
    PUBLISHER  = "publisher"
    SCHOOL  = "school"
    SERIES  = "series"
    TITLE  = "title"
    TYPE  = "type"
    URL = "url"
    VOLUME  = "volume"
    YEAR  = "year"

def get_entries(source_file: str) -> list[Entry]:
    """ Gets a list of entry objects from a bibtex file

    Args:
        source_file (str): Path to the bibtex file

    Returns:
        list[Entry]: List of entries
    """
    result = []
    bibtex_data = parse_file(source_file)
    source_file_no_ext = os.path.splitext(os.path.basename(source_file))[0]
    for entry in bibtex_data.entries.values():
        result.append(
                Entry(
                    ResourceData(entry.fields.get(Fields.DOI, ""), entry.fields.get(Fields.ISBN, ""), entry.fields.get(Fields.TITLE, ""), entry.fields.get(Fields.ABSTRACT, ""), entry.fields.get(Fields.KEYWORDS, "").replace(",", " |")),
                    [EntrySource(source_file_no_ext, entry.fields.get(Fields.URL, ""))],
                )
            )

    return result
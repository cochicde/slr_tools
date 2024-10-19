from enum import StrEnum
from pybtex.database import parse_file

from database.entry import Entry, EntrySource
from literature.data import ResourceData

class Fields(StrEnum):
    ADDRESS  = "address"
    ANNOTE  = "annote"
    AUTHOR  = "author"
    BOOKTITLE  = "booktitle"
    CHAPTER  = "chapter"
    CROSSREF  = "crossref"
    EDITION  = "edition"
    EDITOR  = "editor"
    HOWPUBLISHED  = "howpublished"
    INSTITUTION  = "institution"
    JOURNAL  = "journal"
    KEY  = "key"
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
    VOLUME  = "volume"
    YEAR  = "year"
    ABSTRACT  = "abstract"
    DOI = "doi"
    ISBN = "isbn"
    KEYWORDS = "keywords"
    URL = "url"

def get_entries(source_file: str):
    result = []
    bibtex_data = parse_file(source_file)
    for entry in bibtex_data.entries.values():
        result.append(
                Entry(
                    ResourceData(entry.fields.get(Fields.DOI, ""), entry.fields.get(Fields.ISBN, ""), entry.fields.get(Fields.TITLE, ""), entry.fields.get(Fields.ABSTRACT, ""), entry.fields.get(Fields.KEYWORDS, "").replace(",", " |")),
                    [EntrySource("acm", entry.fields.get(Fields.URL, ""))],
                )
            )

    return result
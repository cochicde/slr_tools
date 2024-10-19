import requests

from database.entry import Entry, EntrySource
from database.remote.connectors.connector import Connector
from literature.data import ResourceData, ResourceFields
from parameters.provider import Provider


class Parameters(Provider):
    NAME = "ieee"

    def get_parameters() -> dict:
        parameters = Provider.get_parameters(Parameters.NAME)
        if "token" not in parameters:
            raise Exception("Missing token to connect to the IEEE API")

        return parameters


class IEEEConnector(Connector):
    __API_URI__ = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
    __FIELDS_MAP = {
        ResourceFields.DOI: "doi",
        ResourceFields.ISBN: "isbn",
        ResourceFields.TITLE: "title",
        ResourceFields.ABSTRACT: "abstract",
        ResourceFields.KEYWORDS: "index_terms", # author_terms [object] -> terms [array] 
        "link": "html_url",
    }

    def __init__(self, query: str) -> None:
        ieee_parameters = Parameters.get_parameters()
        self.token = ieee_parameters["token"]
        self.query = query
        self.start_record = 1

    def request_first(self) -> list[Entry]:
        return self.request_next()

    def request_next(self) -> list[Entry]:
        response = self.__make_api_call()
        return self.__parse_response(response)

    def __make_api_call(self) -> str:
        parameters = dict(
            apikey=self.token,
            querytext=self.query,
            start_record=self.start_record
        )
        response = requests.get(
            url=IEEEConnector.__API_URI__, params=parameters,
        )

        if not response.ok:
            return response.raise_for_status()

        return response.json()

    def __parse_response(self, response: dict) -> list[Entry]:
        to_return = []
        for entry in response["articles"]:
            doi = entry.get(IEEEConnector.__FIELDS_MAP[ResourceFields.DOI], "")
            isbn = entry.get(IEEEConnector.__FIELDS_MAP[ResourceFields.ISBN], "")
            title = entry.get(IEEEConnector.__FIELDS_MAP[ResourceFields.TITLE], "")
            abstract = entry.get(
                IEEEConnector.__FIELDS_MAP[ResourceFields.ABSTRACT], ""
            )
            terms = entry.get(
                IEEEConnector.__FIELDS_MAP[ResourceFields.KEYWORDS], {}
            )
            author_terms = terms.get("author_terms", {})

            keywords = ' | '.join(author_terms.get("terms", []))

            link = entry.get(IEEEConnector.__FIELDS_MAP["link"], "")

            to_return.append(
                Entry(
                    ResourceData(doi, isbn, title, abstract, keywords),
                    [EntrySource(Parameters.NAME, link)],
                )
            )
        self.start_record = self.start_record + len(response["articles"])
        return to_return

   
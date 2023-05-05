import requests

from database.remote.connectors.connector import Connector
from literature.data import ResourceData, ResourceFields
from parameters.provider import Provider


class Parameters(Provider):
    NAME = "scopus"

    def get_parameters() -> dict:
        parameters = Provider.get_parameters(Parameters.NAME)
        if "token" not in parameters:
            raise Exception("Missing token to connect to the Scopus API")

        return parameters


class ScopusConnector(Connector):
    __API_URI__ = "https://api.elsevier.com/content/search/scopus"
    __FIELDS_MAP = {
        ResourceFields.DOI: "prism:doi",
        ResourceFields.TITLE: "dc:title",
        ResourceFields.LINK: "prism:url",
        ResourceFields.ABSTRACT: "dc:description",
        ResourceFields.ISBN: "prism:isbn",
        ResourceFields.ISSN: "prism:issn",
    }

    def __init__(self) -> None:
        scopus_parameters = Parameters.get_parameters()
        self.token = scopus_parameters["token"]
        self.institutional_token = scopus_parameters.get("institutional_token", None)
        self.next_link = None

    def next() -> list[ResourceData]:
        pass

    def __make_api_call(self, query: str) -> str:
        parameters = dict(
            query=query,
            field=",".join(ScopusConnector.__FIELDS_MAP.values()),
            view="COMPLETE",
        )

        headers = {
            "X-ELS-APIKey": self.token,
            "X-ELS-Insttoken": self.institutional_token,
        }

        response = requests.get(
            url=ScopusConnector.__API_URI__, params=parameters, headers=headers
        )
        if not response.ok:
            return response.raise_for_status()

        return response.json()

    def __parse_response(self, response: str) -> list[ResourceData]:
        to_return = []
        for entry in response["search-results"]["entry"]:
            doi = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.DOI], "")
            title = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.TITLE], "")
            link = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.LINK], "")
            abstract = entry.get(
                ScopusConnector.__FIELDS_MAP[ResourceFields.ABSTRACT], ""
            )
            issn = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.ISSN], "")
            isbn = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.ISBN], "")

            # isbn returns as an 1-element array of an object which has the actual isbn number under the '$' field
            if isbn != "":
                isbn = isbn[0]["$"]

            if title == "" or doi == "" or link == "":
                print(
                    "warning: some data is not valid:\nDOI: " + doi,
                    "\ntitle: " + title + "\nlink: " + link,
                )

            to_return.append(ResourceData(doi, title, abstract, link, issn, isbn))
        return to_return

    def request(self, query: str) -> list[ResourceData]:
        self.next_link = None
        response = self.__make_api_call(query)
        return self.__parse_response(response)

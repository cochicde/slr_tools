import requests

from database.entry import Entry, EntrySource
from loader.remote.connectors.connector import Connector
from model.resource import ResourceData, ResourceFields
from loader.remote.parameters import Parameters


class Parameters(Parameters):
    NAME = "scopus"

    def get_parameters() -> dict:
        parameters = Parameters.get_parameters(Parameters.NAME)
        if "token" not in parameters:
            raise Exception("Missing token to connect to the Scopus API")

        return parameters


class ScopusConnector(Connector):
    __API_URI__ = "https://api.elsevier.com/content/search/scopus"
    __FIELDS_MAP = {
        ResourceFields.DOI: "prism:doi",
        ResourceFields.ISBN: "prism:isbn",
        ResourceFields.TITLE: "dc:title",
        ResourceFields.ABSTRACT: "dc:description",
        ResourceFields.KEYWORDS: "authkeywords",
        "link": "prism:url",
    }

    def __init__(self, query: str) -> None:
        scopus_parameters = Parameters.get_parameters()
        self.token = scopus_parameters["token"]
        self.institutional_token = scopus_parameters.get("institutional_token", None)
        self.partner_id = scopus_parameters.get("partner_id", None)
        self.query = query
        self.next_link = None

    def request_first(self) -> list[Entry]:
        response = self.__make_api_call(True)
        return self.__parse_response(response)

    def request_next(self) -> list[Entry]:
        response = self.__make_api_call(False)
        return self.__parse_response(response)

    def __make_api_call(self, first: bool) -> str:
        headers = {
            "X-ELS-APIKey": self.token,
            "X-ELS-Insttoken": self.institutional_token,
        }

        if first:
            return self.__make_first_api_call(headers)
        else:
            return self.__make_next_api_call(headers)

    def __make_first_api_call(self, headers: dict) -> str:
        parameters = dict(
            query=self.query,
            field=",".join(ScopusConnector.__FIELDS_MAP.values()),
            view="COMPLETE",
            cursor="*",
        )
        response = requests.get(
            url=ScopusConnector.__API_URI__, params=parameters, headers=headers
        )

        if not response.ok:
            return response.raise_for_status()

        return response.json()

    def __make_next_api_call(self, headers: dict) -> str:
        if self.next_link is None:
            return {}
        response = requests.get(url=self.next_link, headers=headers)

        if not response.ok:
            return response.raise_for_status()

        return response.json()

    def __parse_response(self, response: dict) -> list[Entry]:
        if (
            "search-results" not in response
            or "entry" not in response["search-results"]
            or "error" in response["search-results"]["entry"][0]
        ):
            self.next_link = None
            return []

        self.next_link = None

        for link in response["search-results"]["link"]:
            if link["@ref"] == "next":
                self.next_link = link["@href"]
                break

        to_return = []
        for entry in response["search-results"]["entry"]:
            doi = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.DOI], "")
            isbn = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.ISBN], "")
            title = entry.get(ScopusConnector.__FIELDS_MAP[ResourceFields.TITLE], "")
            abstract = entry.get(
                ScopusConnector.__FIELDS_MAP[ResourceFields.ABSTRACT], ""
            )
            keywords = entry.get(
                ScopusConnector.__FIELDS_MAP[ResourceFields.KEYWORDS], ""
            )
            link = entry.get(ScopusConnector.__FIELDS_MAP["link"], "")

            # isbn returns as an 1-element array of an object which has the actual isbn number under the '$' field
            if isbn != "":
                isbn = isbn[0]["$"]

            to_return.append(
                Entry(
                    ResourceData(doi, isbn, title, abstract, keywords),
                    [EntrySource(Parameters.NAME, self.__transform_link(link))],
                )
            )
        return to_return

    # Getting the direct link from Scopus is not easy. The field "link ref=scoups" does not return anything
    # We get the link by getting the api link to the resource and manually create the link based on previous
    # knowledge of the link format form scopus
    #  e.g.:
    #       from -> https://api.elsevier.com/content/abstract/scopus_id/85149120151
    #       to -> https://www.scopus.com/inward/record.uri?partnerID=HzOxMe3b&scp=85149120151'
    def __transform_link(self, link: str) -> str:
        if self.partner_id is None:
            return link

        id = link.split("/")[-1]
        return (
            "https://www.scopus.com/inward/record.uri?partnerID="
            + self.partner_id
            + "&scp="
            + id
        )

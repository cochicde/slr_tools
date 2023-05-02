from database.remote.connectors.scopus import ScopusConnector
from literature.data import ResourceData
from query.exporter.scopus import ScopusQuery
from query.exporter.serializer import get_query_string
from query.model.query import Query


class ScopusDatabase:
    def __init__(self) -> None:
        self.connector = ScopusConnector()
        self.query_exporter = ScopusQuery

    def request(self, query: str) -> list[ResourceData]:
        return self.connector.request(query)

    def request(self, query: Query) -> list[ResourceData]:
        return self.connector.request(get_query_string(query, self.query_exporter))

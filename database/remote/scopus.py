from database.remote.connectors.scopus import ScopusConnector
from literature.data import ResourceData
from query.exporter.scopus import ScopusQuery
from query.exporter.serializer import get_query_string
from query.model.query import Query


class ScopusDatabase:
    def __init__(self, query: str) -> None:
        self.connector = ScopusConnector(query)

    def __init__(self, query: Query) -> None:
        self.connector = ScopusConnector(get_query_string(query, ScopusQuery))

    def request_all(self) -> list[ResourceData]:
        return self.connector.request_all()

    def request_first(self) -> list[ResourceData]:
        return self.connector.request_first()

    def request_next(self) -> list[ResourceData]:
        return self.connector.request_next()

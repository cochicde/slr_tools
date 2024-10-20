from loader.remote.connectors.ieee import IEEEConnector
from model.resource import ResourceData
from query.exporter.ieee import IEEEQuery
from query.exporter.serializer import get_query_string
from query.model.query import Query


class IEEE:
    def __init__(self, query: str) -> None:
        self.connector = IEEEConnector(query)

    def __init__(self, query: Query) -> None:
        self.connector = IEEEConnector(get_query_string(query, IEEEQuery))

    def request_all(self) -> list[ResourceData]:
        return self.connector.request_all()

    def request_first(self) -> list[ResourceData]:
        return self.connector.request_first()

    def request_next(self) -> list[ResourceData]:
        return self.connector.request_next()

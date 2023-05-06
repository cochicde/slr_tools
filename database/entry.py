from literature.data import ResourceData


class Entry:
    def __init__(self, resource: ResourceData, link: str):
        self.resource = resource
        self.link = link

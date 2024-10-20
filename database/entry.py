from model.resource import ResourceData


class EntryState:
    """ Information added by the user to an entry. These are all things that a user might want to add/change
    to a scientific resource
    """
  
    def __init__(
        self, rejected: int = 0, save_for_later: bool = False, notes: str = ""
    ) -> None:
        """ Constructor

        Args:
            rejected (int, optional): Rejected value given to the entry. This is also used for entries which are accepted by the user. Defaults to 0.
            save_for_later (bool, optional): Mark the entry as interesting for the future. Defaults to False.
            notes (str, optional): Any notes that user wants to have on the entry. Defaults to "".
        """
        self.rejected = rejected
        self.save_for_later = save_for_later
        self.notes = notes


class EntrySource:
    """ Information about the source of the scientific resource
    """
    def __init__(self, origin: str, link: str) -> None:
        """ Constructor

        Args:
            origin (str): Name given to the source of the scientific resource (e.g. ieee, acm, ...)
            link (str): Link to the scientific resource
        """
        self.origin = origin
        self.link = link

    def __str__(self) -> str:
        """ Get a string representation of the entry source. Useful for debugging.

        Returns:
            str: string representation of the entry source
        """
        return (self.origin + " -> " + self.link if self.link is not None else "empty")


class Entry:
    """ Representation of a row in the database which includes data from the scientific resource, the source of it and its state.
    """
  
    def __init__(
        self,
        resource: ResourceData,
        sources: list[EntrySource],
        state: EntryState = EntryState(),
    ) -> None:
        """ Constructor

        Args:
            resource (ResourceData): Scientific resource information
            sources (list[EntrySource]): Information of the sources where the scientific resource can be found
            state (EntryState, optional): State of the entry. Defaults to EntryState().
        """
        self.resource = resource
        self.sources = sources
        self.state = state

    def __str__(self) -> str:
        """ Get a string representation of the entry. Useful for debugging.

        Returns:
            str: string representation of the entry
        """
        return (str(self.resource) + 
                "\nlinks: " + "\n".join(str(link) for link in self.sources)
                )
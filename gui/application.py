import tkinter as tk
from literature.data import ResourceData, ResourceFields
from database.local.sqlite import Sqlite3


class ApplicationGUI:
    def __init__(self, database: str) -> None:
        self.root = tk.Tk()
        self.root.title("Filter Papers")
        # self.root.geometry("1500x1500")
        self.resource_widgets = [None] * (ResourceFields.KEYWORDS.value + 1)

        self.resource_frame = self.__resource_frame(self.root)
        self.resource_frame.pack(fill=tk.BOTH, expand=tk.YES)

        self.database = Sqlite3(database)
        self.entries = self.database.get_not_reviewed().fetchall()

    def __resource_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent, bg="yellow")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=2)

        for field in ResourceFields:
            if field == ResourceFields.ABSTRACT:
                message = tk.Message(frame, bg="red")
                message.bind(
                    "<Configure>", lambda e: message.configure(width=e.width - 10)
                )
                self.resource_widgets[field.value] = message
            else:
                self.resource_widgets[field.value] = tk.Label(
                    frame, bg="red", text="---"
                )

        self.resource_widgets[ResourceFields.TITLE.value].grid(
            row=0, column=0, sticky="w"
        )
        self.resource_widgets[ResourceFields.KEYWORDS.value].grid(
            row=1, column=0, sticky="w"
        )
        self.resource_widgets[ResourceFields.DOI.value].grid(
            row=2, column=0, sticky="w"
        )
        self.resource_widgets[ResourceFields.ISBN.value].grid(
            row=2, column=1, sticky="w"
        )
        self.resource_widgets[ResourceFields.ABSTRACT.value].grid(
            row=3,
            column=0,
            sticky="we",
        )

        return frame

    def launch(self):
        self.root.mainloop()

    def load(self, resource: ResourceData):
        self.resource_widgets[ResourceFields.DOI.value].config(text=resource.doi)
        self.resource_widgets[ResourceFields.ISBN.value].config(text=resource.isbn)
        self.resource_widgets[ResourceFields.TITLE.value].config(text=resource.title)
        self.resource_widgets[ResourceFields.ABSTRACT.value].config(
            text=resource.abstract
        )
        self.resource_widgets[ResourceFields.KEYWORDS.value].config(
            text=resource.keywords
        )

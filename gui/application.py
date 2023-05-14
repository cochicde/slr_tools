import tkinter as tk
from literature.data import ResourceData, ResourceFields
from database.local.sqlite import Sqlite3
from parameters.provider import Provider


class Parameters(Provider):
    NAME = "gui"

    def get_parameters() -> dict:
        parameters = Provider.get_parameters(Parameters.NAME)
        if "rejected" not in parameters:
            raise Exception("Missing rejected configuration for the GUI")

        return parameters


class ApplicationGUI:
    def __init__(self, database: str) -> None:
        self.root = tk.Tk()
        self.root.title("Filter Papers")
        self.root.bind("<Key>", self.__handle_keystroke)
        self.resource_widgets = [None] * (ResourceFields.KEYWORDS.value + 1)

        self.resource_frame = self.__resource_frame(self.root)
        # self.resource_frame.pack(fill=tk.BOTH, expand=tk.YES)
        self.resource_frame.pack()

        self.links = tk.Message(self.root)
        self.links.pack()

        self.rejected_frame = self.__rejected_frame(self.root)
        self.rejected_frame.pack()

        self.later_frame = self.__save_for_later_frame(self.root)
        self.later_frame.pack()

        self.previous = tk.Button(
            self.root, text="Previous", command=self.go_to_previous
        )
        self.previous.pack()

        self.next = tk.Button(self.root, text="Next", command=self.go_to_next)
        self.next.pack()

        self.old_state = None

        self.database = Sqlite3(database)
        self.entries = self.database.get_not_reviewed()

        if len(self.entries) != 0:
            self.current_pos = 0
            self.__load_current()
        else:
            self.current_pos = None

    def __check_and_update_state(self):
        if self.old_state is None:
            return

        something_changed = False
        if self.old_state.save_for_later != self.later.get():
            # update database
            self.database.update_save_for_later(
                self.entries[self.current_pos][0], self.later.get()
            )

            # update cache
            self.entries[self.current_pos][1].state.save_for_later = self.later.get()
            something_changed = True

        if self.old_state.rejected != self.rejected.get():
            # update database
            self.database.update_rejected(
                self.entries[self.current_pos][0], self.rejected.get()
            )

            # update cache
            self.entries[self.current_pos][1].state.rejected = self.later.get()
            something_changed = True

        if something_changed:
            self.database.save()

    def go_to_previous(self):
        self.__check_and_update_state()

        if self.current_pos is None:
            if len(self.entries) != 0:
                self.current_pos = 0
            else:
                return
        else:
            if self.current_pos == 0:
                self.current_pos = len(self.entries) - 1
            else:
                self.current_pos -= 1

        self.__load_current()

    def go_to_next(self):
        self.__check_and_update_state()

        if self.current_pos is None:
            if len(self.entries) != 0:
                self.current_pos = 0
            else:
                return
        else:
            if self.current_pos == len(self.entries) - 1:
                self.current_pos = 0
            else:
                self.current_pos += 1

        self.__load_current()

    def __handle_keystroke(self, event):
        if event.keysym == "Right":
            self.go_to_next()
        elif event.keysym == "Left":
            self.go_to_previous()
        elif event.keysym == "s":
            self.later.set(True)
        elif event.keysym == "d":
            self.later.set(False)
        else:
            try:
                number = int(event.keysym)
                self.rejected.set(number)
            except:
                pass

    def __rejected_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)
        self.rejected = tk.IntVar()
        reasons = Parameters.get_parameters()["rejected"].strip("][").split(", ")
        for value, reason in enumerate(reasons):
            tk.Radiobutton(
                frame,
                text=reason + " (" + str(value) + ")",
                value=value,
                variable=self.rejected,
            ).pack()

        return frame

    def __save_for_later_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)
        self.later = tk.BooleanVar()

        tk.Radiobutton(
            frame, text="Save for later", value=True, variable=self.later
        ).pack()

        tk.Radiobutton(
            frame, text="Don't save for later", value=False, variable=self.later
        ).pack()

        return frame

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

    def __load_current(self):
        data = self.entries[self.current_pos][1]
        self.resource_widgets[ResourceFields.DOI.value].config(text=data.resource.doi)
        self.resource_widgets[ResourceFields.ISBN.value].config(text=data.resource.isbn)
        self.resource_widgets[ResourceFields.TITLE.value].config(
            text=data.resource.title
        )
        self.resource_widgets[ResourceFields.ABSTRACT.value].config(
            text=data.resource.abstract
        )
        self.resource_widgets[ResourceFields.KEYWORDS.value].config(
            text=data.resource.keywords
        )

        self.rejected.set(0 if data.state.rejected is None else data.state.rejected)

        self.later.set(True if data.state.save_for_later is True else False)

        links = ""
        for source in data.sources:
            if source.link is not None:
                links += source.link + "\n"

        self.links.config(text=links)

        self.old_state = data.state

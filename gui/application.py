import tkinter as tk
from literature.data import ResourceData, ResourceFields
from database.local.sqlite import Sqlite3
from parameters.provider import Provider
import webbrowser


class Parameters(Provider):
    NAME = "gui"

    def get_parameters() -> dict:
        parameters = Provider.get_parameters(Parameters.NAME)
        if "rejected" not in parameters:
            raise Exception("Missing rejected configuration for the GUI")

        return parameters


class ApplicationGUI:
    __LINKS_INDEX = ResourceFields.KEYWORDS.value + 1

    def __init__(self, database: str) -> None:
        self.root = tk.Tk()
        self.root.title("Filter Papers")
        self.root.bind("<Key>", self.__handle_keystroke)

        self.resource_widgets = [None] * (ApplicationGUI.__LINKS_INDEX + 1)

        self.resource_frame = self.__resource_frame(self.root)
        self.resource_frame.grid(row=0, column=0, padx=15, pady=15)

        right_frame = tk.Frame(self.root)

        self.rejected_frame = self.__rejected_frame(right_frame)
        # self.rejected_frame.grid(row=1, column=1)
        self.rejected_frame.pack()

        self.later_frame = self.__save_for_later_frame(right_frame)
        # self.later_frame.grid(row=0, column=1)
        self.later_frame.pack(pady=10)

        right_frame.grid(column=1, row=0, sticky="n", padx=15, pady=15)

        buttons_frame = tk.Frame(right_frame)

        self.previous = tk.Button(
            buttons_frame, text="Previous", command=self.go_to_previous
        )
        self.previous.grid(row=0, column=0, sticky="e")

        self.next = tk.Button(buttons_frame, text="Next", command=self.go_to_next)
        self.next.grid(row=0, column=1, sticky="w")

        buttons_frame.pack(pady=15)

        change_font_frame = tk.Frame(right_frame)

        self.change_font_label = tk.Label(
            change_font_frame, text="Change Abstract Font"
        )

        self.change_font_label.grid(row=0, column=0, columnspan=2)

        self.decrease = tk.Button(
            change_font_frame, text="-", command=lambda: self.__change_font(False)
        )
        self.decrease.grid(row=1, column=0, sticky="e")

        self.increase = tk.Button(
            change_font_frame, text="+", command=lambda: self.__change_font(True)
        )
        self.increase.grid(row=1, column=1, sticky="w")
        change_font_frame.pack(pady=15)

        self.old_state = None

        self.database = Sqlite3(database)
        self.entries = self.database.get_not_reviewed()

        if len(self.entries) != 0:
            self.current_pos = 0
            self.__load_current()
        else:
            self.current_pos = None

    def __change_font(self, increase: bool) -> None:
        font_type, font_size = (
            self.resource_widgets[ResourceFields.ABSTRACT.value].cget("font").split(" ")
        )

        if increase:
            font_size = int(font_size) + 1
        else:
            font_size = int(font_size) - 1

        self.resource_widgets[ResourceFields.ABSTRACT.value].config(
            font=(font_type, font_size)
        )

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
            self.entries[self.current_pos][1].state.rejected = self.rejected.get()
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
        elif event.keysym == "plus":
            self.__change_font(True)
        elif event.keysym == "minus":
            self.__change_font(False)
        else:
            try:
                number = int(event.keysym)
                if number <= self.max_rejected:
                    self.rejected.set(number)
            except:
                pass

    def __rejected_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)
        self.rejected = tk.IntVar()
        reasons = Parameters.get_parameters()["rejected"].strip("][").split(", ")
        self.max_rejected = len(reasons) - 1

        row = 0
        for value, reason in enumerate(reasons):
            tk.Radiobutton(
                frame,
                text=reason + " (" + str(value) + ")",
                value=value,
                variable=self.rejected,
            ).grid(row=row, column=0, sticky="w")
            row += 1

        return frame

    def __save_for_later_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)
        self.later = tk.BooleanVar()

        tk.Radiobutton(
            frame, text="Save for later (s)", value=True, variable=self.later
        ).grid(row=0, column=0, sticky="w")

        tk.Radiobutton(
            frame, text="Don't save for later (d)", value=False, variable=self.later
        ).grid(row=1, column=0, sticky="w")

        return frame

    def __resource_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=2)

        wraplength = 1000

        tk.Label(frame, text="Title").grid(row=0, column=0, sticky="e")
        tk.Label(frame, text="Keywords").grid(row=1, column=0, sticky="e")
        tk.Label(frame, text="DOI").grid(row=2, column=0, sticky="e")
        tk.Label(frame, text="ISBN").grid(row=3, column=0, sticky="e")
        tk.Label(frame, text="Links").grid(row=4, column=0, sticky="e")
        self.abstract_label = tk.Label(frame, text="Abstract")
        self.abstract_label.grid(row=5, column=0, sticky="e")

        title = tk.Label(frame, text="---", wraplength=wraplength)
        title.grid(row=0, column=1, sticky="w")
        self.resource_widgets[ResourceFields.TITLE.value] = title

        keywords = tk.Label(frame, text="---", wraplength=wraplength)
        keywords.grid(row=1, column=1, sticky="w")
        self.resource_widgets[ResourceFields.KEYWORDS.value] = keywords

        doi = tk.Label(frame, text="---")
        doi.grid(row=2, column=1, sticky="w")
        self.resource_widgets[ResourceFields.DOI.value] = doi

        isbn = tk.Label(frame, text="---", wraplength=wraplength)
        isbn.grid(row=3, column=1, sticky="w")
        self.resource_widgets[ResourceFields.ISBN.value] = isbn

        links = tk.Label(frame, text="---", justify="left", wraplength=wraplength)
        links.grid(row=4, column=1, sticky="w", rowspan=1)

        self.resource_widgets[ApplicationGUI.__LINKS_INDEX] = [links]

        # Abstract
        abstract = tk.Label(
            frame, wraplength=wraplength, justify="left", font=("Arial", 20)
        )
        self.resource_widgets[ResourceFields.ABSTRACT.value] = abstract
        abstract.grid(row=5, column=1, sticky="w")

        return frame

    def launch(self):
        self.root.mainloop()

    def __open_link(self, url):
        webbrowser.open(url)

    def __load_current(self):
        data = self.entries[self.current_pos][1]
        self.resource_widgets[ResourceFields.DOI.value].config(text=data.resource.doi)
        self.resource_widgets[ResourceFields.ISBN.value].config(text=data.resource.isbn)
        self.resource_widgets[ResourceFields.TITLE.value].config(
            text=data.resource.title
        )

        self.resource_widgets[ResourceFields.KEYWORDS.value].config(
            text=data.resource.keywords
        )

        for label in self.resource_widgets[ApplicationGUI.__LINKS_INDEX]:
            label.destroy()

        self.resource_widgets[ApplicationGUI.__LINKS_INDEX] = []

        row = 4
        for source in data.sources:
            if source.link is not None:
                link = tk.Label(
                    self.resource_frame,
                    text=source.link,
                    justify="left",
                    cursor="hand2",
                )
                link.grid(row=row, column=1, sticky="w")
                link.bind(
                    "<Button-1>", lambda event, link=source.link: self.__open_link(link)
                )
                self.resource_widgets[ApplicationGUI.__LINKS_INDEX].append(link)
                row += 1

        self.resource_widgets[ResourceFields.ABSTRACT.value].config(
            text=data.resource.abstract
        )

        self.resource_widgets[ResourceFields.ABSTRACT.value].grid(row=row)
        self.abstract_label.grid(row=row)

        self.rejected.set(0 if data.state.rejected is None else data.state.rejected)

        self.later.set(True if data.state.save_for_later is True else False)

        self.old_state = data.state

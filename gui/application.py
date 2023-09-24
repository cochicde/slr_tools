import tkinter as tk
from literature.data import ResourceData, ResourceFields
from database.local.sqlite import Sqlite3
from parameters.provider import Provider
import webbrowser
import re


class Parameters(Provider):
    NAME = "gui"

    def get_parameters() -> dict:
        parameters = Provider.get_parameters(Parameters.NAME)
        if "rejected" not in parameters:
            raise Exception("Missing rejected configuration for the GUI")

        return parameters


class CustomText(tk.Text):
    """
    Wrapper for the tkinter.Text widget with additional methods for
    highlighting and matching regular expressions.

    highlight_all(pattern, tag) - Highlights all matches of the pattern.
    highlight_pattern(pattern, tag) - Cleans all highlights and highlights all matches of the pattern.
    clean_highlights(tag) - Removes all highlights of the given tag.
    search_re(pattern) - Uses the python re library to match patterns.
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master

        # sample tag
        self.tag_config("match", background="yellow")

    def highlight(self, tag, start, end):
        self.tag_add(tag, start, end)

    def highlight_all(self, pattern, tag):
        for match in self.search_re(pattern):
            self.highlight(tag, match[0], match[1])

    def clean_highlights(self, tag):
        self.tag_remove(tag, "1.0", tk.END)

    def search_re(self, pattern):
        """
        Uses the python re library to match patterns.

        Arguments:
            pattern - The pattern to match.
        Return value:
            A list of tuples containing the start and end indices of the matches.
            e.g. [("0.4", "5.9"]
        """
        matches = []
        text = self.get("1.0", tk.END).splitlines()
        for i, line in enumerate(text):
            for match in re.finditer(pattern, line):
                matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))

        return matches

    def highlight_pattern(self, pattern, tag="match"):
        """
        Cleans all highlights and highlights all matches of the pattern.

        Arguments:
            pattern - The pattern to match.
            tag - The tag to use for the highlights.
        """
        self.clean_highlights(tag)
        self.highlight_all(pattern, tag)


class ApplicationGUI:
    __LINKS_INDEX = ResourceFields.KEYWORDS.value + 1

    def __init__(self, database: str) -> None:
        self.root = tk.Tk()
        self.root.title("Filter Papers")
        self.root.bind("<Key>", self.__handle_keystroke)
        self.root.geometry(
            str(self.root.winfo_screenwidth())
            + "x"
            + str(self.root.winfo_screenheight())
        )
        self.root.tk_setPalette(background="white")

        padx = 5
        pady = 5

        self.resource_frame = self.__resource_frame(self.root)
        self.resource_frame.grid(row=0, column=0, sticky="nw", padx=padx, pady=pady)

        self.right_frame = self.__right_frame(self.root)
        self.right_frame.grid(column=1, row=0, sticky="ne", padx=padx, pady=pady)

        self.root.columnconfigure(0, weight=8)
        self.root.columnconfigure(1, weight=2)

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
            if (
                self.right_frame.winfo_rootx()
                + self.right_frame.winfo_width()
                + self.right_frame.grid_info()["padx"]
                >= self.root.winfo_screenwidth()
            ):
                return
            font_size = int(font_size) + 1
        else:
            font_size = int(font_size) - 1
            if font_size <= 0:
                font_size = 1

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

        # tk adds a newline when inserting into a text for some reason
        current_notes = self.notes.get(1.0, tk.END)[:-1]
        if self.old_state.notes != current_notes:
            # update database
            self.database.update_notes(self.entries[self.current_pos][0], current_notes)

            # update cache
            self.entries[self.current_pos][1].state.notes = current_notes
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

    def __handle_tab_in_text(self, event):
        self.root.focus_set()
        return "break"

    def __update_highlight(self):
        highlight = lambda widget: widget.highlight_pattern(
            self.search_bar.get(1.0, tk.END)[:-1]
        )

        highlight(self.resource_widgets[ResourceFields.ABSTRACT.value])
        highlight(self.resource_widgets[ResourceFields.TITLE.value])
        highlight(self.resource_widgets[ResourceFields.KEYWORDS.value])

    def __handle_keystroke(self, event):
        if event.keysym == "Escape":
            self.root.focus_set()

        if self.root.focus_get() == self.search_bar:
            self.__update_highlight()
        elif self.root.focus_get() != self.notes:
            if event.keysym == "Right" or event.keysym == "Return":
                self.go_to_next()
            elif event.keysym == "Left":
                self.go_to_previous()
            elif event.keysym == "s":
                self.later.set(True)
            elif event.keysym == "d":
                self.later.set(False)
            elif event.keysym == "t":
                self.notes.focus_set()
            elif event.keysym == "plus":
                self.__change_font(True)
            elif event.keysym == "minus":
                self.__change_font(False)
            elif event.keysym == "Down":
                current = self.rejected.get()
                if current >= self.max_rejected:
                    current = 0
                else:
                    current += 1
                self.rejected.set(current)
            elif event.keysym == "Up":
                current = self.rejected.get()
                if current == 0:
                    current = self.max_rejected
                else:
                    current -= 1
                self.rejected.set(current)

            else:
                try:
                    number = int(event.keysym)
                    if number <= self.max_rejected:
                        self.rejected.set(number)
                        self.go_to_next()
                except:
                    pass

    def __resource_frame(self, parent) -> tk.Frame:
        self.resource_widgets = [None] * (ApplicationGUI.__LINKS_INDEX + 1)

        frame = tk.Frame(parent)

        wraplength = 850

        tk.Label(frame, text="Title").grid(row=0, column=0, sticky="e")
        tk.Label(frame, text="Keywords").grid(row=1, column=0, sticky="e")
        tk.Label(frame, text="DOI").grid(row=2, column=0, sticky="e")
        tk.Label(frame, text="ISBN").grid(row=3, column=0, sticky="e")
        tk.Label(frame, text="Links").grid(row=4, column=0, sticky="e")
        self.abstract_label = tk.Label(frame, text="Abstract")
        self.abstract_label.grid(row=6, column=0, sticky="en")

        title = CustomText(frame, width=120, height=1, font="TkDefaultFont")
        title.grid(row=0, column=1, sticky="w")
        self.resource_widgets[ResourceFields.TITLE.value] = title

        keywords = CustomText(frame, width=120, height=1, font="TkDefaultFont")
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

        self.search_bar = tk.Text(
            frame,
            width=80,
            height=1,
            font=("Arial", 16),
            highlightbackground="gray",
            highlightthickness=1,
        )
        self.search_bar.grid(row=5, column=1, sticky="w")
        self.search_bar.insert(
            tk.END,
            "[pP][lL][cC]|[pP]rogram|[lL]ogic|[cC]ontrol|[sS]oftware|[dD]ebug",
        )

        # Abstract
        abstract = CustomText(
            frame,
            wrap="word",
            width=80,
            height=20,
            font=("Arial", 24),
        )
        self.resource_widgets[ResourceFields.ABSTRACT.value] = abstract

        abstract.grid(row=6, column=1, sticky="w")

        return frame

    def __right_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)

        self.counter = tk.Label(frame)
        self.counter.pack(fill=tk.BOTH)

        rejected_frame = self.__rejected_frame(frame)
        rejected_frame.pack(fill=tk.BOTH)

        later_frame = self.__save_for_later_frame(frame)
        later_frame.pack(fill=tk.BOTH, pady=10)

        change_font_frame = self.__change_font_name(frame)
        change_font_frame.pack(pady=15)

        notes_frame = self.__notes_frame(frame)
        notes_frame.pack(pady=15, fill=tk.BOTH)

        buttons_frame = self.__next_previous_frame(frame)
        buttons_frame.pack(pady=15)

        return frame

    def __rejected_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)
        self.rejected = tk.IntVar()
        reasons = Parameters.get_parameters()["rejected"].strip("][").split(", ")
        self.max_rejected = len(reasons) - 1

        row = 0
        for value, reason in enumerate(reasons):
            tk.Radiobutton(
                frame,
                text=reason[1:-1] + " (" + str(value) + ")",
                value=value,
                variable=self.rejected,
            ).grid(row=row, column=0, sticky="w")
            row += 1

        return frame

    def __save_for_later_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)
        self.later = tk.BooleanVar()

        tk.Radiobutton(
            frame, text="Don't save for later (d)", value=False, variable=self.later
        ).grid(row=0, column=0, sticky="w")

        tk.Radiobutton(
            frame, text="Save for later (s)", value=True, variable=self.later
        ).grid(row=1, column=0, sticky="w")

        return frame

    def __change_font_name(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)

        self.change_font_label = tk.Label(frame, text="Change Abstract Font")

        self.change_font_label.grid(row=0, column=0, columnspan=2)

        self.decrease = tk.Button(
            frame, text="-", command=lambda: self.__change_font(False)
        )
        self.decrease.grid(row=1, column=0, sticky="e")

        self.increase = tk.Button(
            frame, text="+", command=lambda: self.__change_font(True)
        )
        self.increase.grid(row=1, column=1, sticky="w")

        return frame

    def __notes_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)

        notes_label = tk.Label(frame, text="Notes (t)")
        notes_label.pack(fill=tk.BOTH)

        self.notes = tk.Text(
            frame,
            wrap="word",
            width=10,
            font=("Arial", 15),
            height=10,
            highlightbackground="gray",
            highlightthickness=1,
        )
        self.notes.bind("<Tab>", self.__handle_tab_in_text)
        self.notes.pack(fill=tk.BOTH)

        return frame

    def __next_previous_frame(self, parent) -> tk.Frame:
        frame = tk.Frame(parent)

        self.previous = tk.Button(frame, text="Previous", command=self.go_to_previous)
        self.previous.grid(row=0, column=0, sticky="e")

        self.next = tk.Button(frame, text="Next", command=self.go_to_next)
        self.next.grid(row=0, column=1, sticky="w")

        frame.pack(pady=15)

        return frame

    def launch(self):
        self.root.mainloop()

    def __open_link(self, url):
        webbrowser.open(url)

    def __update_widget_text(self, widget, text):
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)

    def __load_current(self):
        data = self.entries[self.current_pos][1]

        self.counter.config(text=str(self.current_pos + 1))

        doi = self.resource_widgets[ResourceFields.DOI.value]
        doi.config(text=data.resource.doi)
        doi.bind(
            "<Button-1>",
            lambda event, link="https://doi.org/" + data.resource.doi: self.__open_link(
                link
            ),
        )
        doi.config(cursor="hand2")
        self.resource_widgets[ResourceFields.ISBN.value].config(text=data.resource.isbn)
        self.__update_widget_text(
            self.resource_widgets[ResourceFields.TITLE.value], data.resource.title
        )

        self.__update_widget_text(
            self.resource_widgets[ResourceFields.KEYWORDS.value], data.resource.keywords
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

        row += 1  # skip search bar

        abstract = self.resource_widgets[ResourceFields.ABSTRACT.value]
        self.resource_widgets[ResourceFields.ABSTRACT.value].config(state="normal")
        self.__update_widget_text(
            self.resource_widgets[ResourceFields.ABSTRACT.value], data.resource.abstract
        )

        self.resource_widgets[ResourceFields.ABSTRACT.value].config(state="disabled")
        self.resource_widgets[ResourceFields.ABSTRACT.value].grid(row=row)
        self.abstract_label.grid(row=row)

        self.rejected.set(0 if data.state.rejected is None else data.state.rejected)

        self.later.set(True if data.state.save_for_later is True else False)

        self.notes.delete(1.0, tk.END)
        self.notes.insert(tk.END, data.state.notes)

        self.__update_highlight()

        self.old_state = data.state

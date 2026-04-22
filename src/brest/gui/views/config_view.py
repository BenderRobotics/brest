import tkinter as tk

from tkinter import Frame, Button
from tkinter.ttk import Notebook


class ConfigView(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, **kwargs)

        self.pack(expand=True, side='right', fill="both")

        # * Action bars
        # TODO layout needs to be automatic, not hardcoded
        self.side_action_bar = Frame(self, width=30)
        self.side_action_bar.pack(side=tk.LEFT, fill=tk.Y)

        self.top_action_bar = Frame(self, height=40, )
        self.top_action_bar.pack(side=tk.TOP, fill=tk.X)

        # * Create tab window
        self.notebook = Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self._fill_top_action_bar()
        self._fill_side_action_bar()

    def add_tab(self, tab, tab_name):
        self.notebook.add(tab, text=tab_name)

    def get_selected_view(self):
        return self.notebook.nametowidget(self.notebook.select())

    def close_selected_tab(self):
        self.notebook.forget(self.notebook.select())

    def _fill_top_action_bar(self):
        """
        Fills button to top action bar
        """
        # ! this lamba should be moved to controller
        swap_button = Button(self.top_action_bar, text="sw",
                             command=lambda: self.get_selected_view().switch_to(('editor', 'config')))
        swap_button.grid(row=0, column=0, pady=5)

        self.create_project_button = Button(self.top_action_bar, text="p+")
        self.create_project_button.grid(row=0, column=1, pady=5, padx=(5, 0))

        self.delete_project_button = Button(self.top_action_bar, text="p-")
        self.delete_project_button.grid(row=0, column=2, pady=5, padx=(5, 0))

        self.create_resource_button = Button(self.top_action_bar, text="r+")
        self.create_resource_button.grid(row=0, column=3, pady=5, padx=(5, 0))

        self.delete_resource_button = Button(self.top_action_bar, text="r-")
        self.delete_resource_button.grid(row=0, column=4, pady=5, padx=(5, 0))

    def _fill_side_action_bar(self):
        """
        Fills button to side action bar
        """
        button_container = Frame(self.side_action_bar)
        button_container.grid(row=0, column=0)
        self.side_action_bar.grid_rowconfigure(0, weight=1)

        self.add_resource_button = Button(button_container, text=">>")
        self.add_resource_button.pack()

        self.delete_resource_button = Button(button_container, text="<<")
        self.delete_resource_button.pack()

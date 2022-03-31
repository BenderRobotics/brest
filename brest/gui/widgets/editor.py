from brest.gui.utilities import TextSyntaxHighlight

import tkinter as tk
from tkinter import Frame, Text, Scrollbar, Canvas, Label


class Editor(Frame):
    def __init__(self, master, content=None):
        Frame.__init__(self, master, file=None)

        self.scrollbar = Scrollbar(master)

        self.area = Text(self, yscrollcommand=self.scrollbar.set)
        self.area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.scrollbar.config(command=self.area.yview)

        self.syntax_highlight = TextSyntaxHighlight(self.area)
        self.syntax_highlight.activate()

        if content:
            self.area.insert("end", content)
            self.syntax_highlight.update(None)

        self.area.bind("<KeyRelease>", self.syntax_highlight.update_line)
        self.area.bind("<Tab>", self._tab)

    def pack(self, **kwargs):
        self.syntax_highlight.activate()
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        Frame.pack(self, kwargs)

    def pack_forget(self):
        self.syntax_highlight.deactivate()
        self.scrollbar.pack_forget()
        Frame.pack_forget(self)

    def _tab(self, *args):
        """
        Overrides tab to place four spaces
        """
        self.area.insert(tk.INSERT, " " * 4)
        return 'break'

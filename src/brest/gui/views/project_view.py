import tkinter as tk
from tkinter import Frame

from brest.gui.widgets import Editor, FrameSwitcher, ScrollableFrame


class ProjectView(FrameSwitcher):
    def __init__(self, master):
        FrameSwitcher.__init__(self, master)

        self.editor = Editor(self)
        self.scrollable_frame = ScrollableFrame(self)

        self.add_frame("scrollable_frame", self.scrollable_frame, expand=True, fill=tk.BOTH)
        self.add_frame("editor", self.editor, expand=True, fill=tk.BOTH)

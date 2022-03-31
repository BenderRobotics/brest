import tkinter as tk

from tkinter import Frame, Canvas
from tkinter.ttk import Scrollbar


class ScrollableFrame(Frame):
    """
    For new items set master to scrollable_frame !
    """
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, kwargs)
        self.canvas = Canvas(self)
        self.scrollbar = Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        # * bind to scrollable_frame size change
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mouse_wheel)

        self._canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", self._on_canvas_size_change)

    def _on_mouse_wheel(self, event):
        # * Get object under cursor and if it is canvas scroll it
        under_cursor = self.winfo_containing(event.x_root, event.y_root)
        if under_cursor == self.canvas:
            self.canvas.yview_scroll(-1 * (event.delta//120), 'units')

    def _on_canvas_size_change(self, event):
        self.canvas.itemconfig(self._canvas_window, width=event.width)

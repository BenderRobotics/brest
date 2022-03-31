import tkinter as tk
from tkinter import Frame, Label
from tkinter.ttk import Treeview, Scrollbar

class ResourceView:
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack(expand=True, side='right', fill="both")

        self.tree = Treeview(self.frame)
        self.tree_scroll = Scrollbar(self.tree)

        self.tree_scroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)

        # * Set up columns
        self.tree['columns'] = ("values")
        self.tree.column("#0", stretch=tk.YES)
        self.tree.heading("#0", text="Resources", anchor=tk.W)
        self.tree.heading("values", text="")

        self.tree.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        item = self.tree.set(self.tree.selection(), 0)
        self.frame.master.master.clipboard_clear()
        self.frame.master.master.clipboard_append(item)
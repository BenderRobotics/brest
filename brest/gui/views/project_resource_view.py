import tkinter as tk
from tkinter import Frame, Label


class ProjectResourceView(Frame):
    def __init__(self, master, name, params, **kwargs):
        Frame.__init__(self, master, bg="orange", **kwargs)
        self.pack(side=tk.TOP, fill=tk.X, expand=True, padx=10, pady=5)

        tk.Label(self, text=name).grid(row=0, column=0, sticky="e")

        self.add_params(params)
        self.columnconfigure(99, weight=1)
        self.columnconfigure(100, minsize=20)

    def add_params(self, params):
        """
        Parent -> None == root
        """
        def add_params_recursive(params, path):
            for key, value in params.items():
                if isinstance(value, dict):
                    self.add_param(path, key)
                    path += "." if path != "" else ""
                    add_params_recursive(value, path + key)
                elif isinstance(value, (list, tuple)):
                    pass
                else:
                    self.add_param(path, key, value)

        add_params_recursive(params, "")

    def _get_target_pos(self, path, row, col):
        """
        Follows path from (row, col) position and return path end position
        if path follow fails, last row position is returned
        """
        if path == "":
            return (0, 0)

        if len(self.grid_slaves(row, col)) > 0:
            widget_text = self.grid_slaves(row, col)[0].cget("text")
            if widget_text == path[0]:
                if len(path) == 1:
                    return (row, col)
                else:
                    return self._get_target_pos(path[1:], row + 1, col + 1)
            else:
                return self._get_target_pos(path, row + 1, col)
        else:
            return row

    def _get_last_pos(self, path, row, col):
        row, col = self._get_target_pos(path, row, col)

        row += 1  # * item can't be next to parent
        while len(self.grid_slaves(row, col + 1)) > 0:
            row += 1

        return (row, col + 1)

    def add_param(self, path, name, value=None):
        def add_line(row, column):
            Label(self, text=name, anchor="w").grid(row=row, column=column, sticky="w")
            if value is not None:
                Label(self, text=value, anchor="e").grid(row=row, column=99, sticky="e")

        if self.grid_size() == (1, 1):
            # * insert first item
            add_line(1, 1)
        else:
            if path != "":
                path = path.split(".")

            row, col = self._get_target_pos(path, 1, 1)

            row += 1  # * item can't be next to parent
            while len(self.grid_slaves(row, col + 1)) > 0:
                if self.grid_slaves(row, col + 1)[0].cget("text") == name:
                    return
                row += 1

            add_line(row, col + 1)

import re
import tkinter as tk


class TextSyntaxHighlight:
    """
    Implement crude syntax highliting of regex based expresions.
    This class does not provide full syntax support just tries to improve readability.
    """

    SYNTAX = [
        {'tag': 'key', 'regex': r"[^:\n]*?:", 'group': 0},            # * any word ending with colon
        {'tag': 'text', 'regex': r"(\".*?\")|(\'.*?\')", 'group': 0},  # * any word between quotes
        {'tag': 'number', 'regex': r"[^:\n]*?:\s*(\d*)\s*$", 'group': 1}
    ]

    def __init__(self, area):
        self.area = area

        # ! create tags referenced in 'SYNTAX'
        self.area.tag_config("key", foreground="green")
        self.area.tag_config("text", foreground="red")
        self.area.tag_config("number", foreground="orange")

        self._active = False

    def _get_line(self, index):
        """
        Returns line number.

        :return type: int
        :returns: line number
        """
        line = index[0]
        end = self._get_line_len(index[1])

        return self.area.get(f"{line}.0", f"{line}.{end}")

    def _get_line_len(self, index):
        """
        Return line len from begining till the EOL.

        :param index: current position -> (line, position)
        :return type: int
        :returns: line length
        """
        line_break = int(index[1])

        char = ''
        while char not in ['\n', '\0']:
            char = self.area.get(f"{index[0]}.{line_break}")
            line_break += 1

        return line_break

    def _get_index(self):
        """
        Returns current position of controlled text area.

        :return type: tuple
        :returns: (line, position)
        """

        return self.area.index(tk.INSERT).split(".")

    def activate(self):
        """
        Activates update method.
        """
        self._active = True

    def deactivate(self):
        """
        Deactivates update method.
        """
        self._active = False

    def remove_highlight(self, index_range):
        """
        Remove any tags (referenced in 'SYNTAX') from text in 'index_range'.
        """
        for rule in self.SYNTAX:
            self.area.tag_remove(rule['tag'], index_range[0], index_range[1])

    def highlight(self, index_range):
        """
        Highlights text in 'index_range' matching regex in 'SYNTAX'.
        """
        line_num = int(index_range[0].split(".")[0])

        content = self.area.get(index_range[0], index_range[1])
        content = content.split("\n")

        for line in content:
            for rule in self.SYNTAX:
                mateches = re.finditer(rule['regex'], line)

                for match in mateches:
                    self.area.tag_add(rule['tag'], f"{line_num}.{match.start(rule['group'])}", f"{line_num}.{match.end(rule['group'])}")
            line_num += 1

    def update_line(self, event):
        """
        Updates current line highliting.
        """
        if self._active:
            index = self._get_index()

            end = self._get_line_len(index)

            index_range = (f"{index[0]}.0", f"{index[0]}.{end}")

            self.remove_highlight(index_range)
            self.highlight(index_range)

    def update(self, event):
        """
        Updates highliting in whole text area.
        """

        if self._active:
            self.remove_highlight(("1.0", "end-1c"))
            self.highlight(("1.0", "end-1c"))

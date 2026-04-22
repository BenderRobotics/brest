from tkinter import Frame


class FrameSwitcher(Frame):
    """
    Switches frames, by raising their contex.
    Before switching, deactivates previous frame.

    TODO iterable, get
    """

    def __init__(self, master):
        Frame.__init__(self, master)

        self._frames = {}
        self._active = None

    def add_frame(self, name, frame, **kwargs):
        """
        Add frame and its unique identifier.
        """
        self._frames.update({name: {'frame': frame, 'kwargs': kwargs}})

        if self._active is None:
            self._active = self._frames[name]
            self._active['frame'].pack(**kwargs)

    def del_frame(self, name):
        """
        Delete frame specified by name.
        """
        if self._active == self._frames[name]:
            for frame_name in self._frames:
                if frame_name != name:
                    self.switch_to(frame_name)
        del self._frames[name]

    def switch_to(self, name):
        """
        Switch to new frame. Deactivates old one and activate new one.
        """

        # * If tupple is passed switches to first non active match
        if isinstance(name, tuple):
            for n in name:
                for fname, value in self._frames.items():
                    if n == fname and value != self._active:
                        self.switch_to(n)
                        return
            return

        if self._active == self._frames[name]:
            return

        self._active['frame'].pack_forget()

        self._active = self._frames[name]

        self._active['frame'].pack(**self._active['kwargs'])

        self._active['frame'].tkraise()

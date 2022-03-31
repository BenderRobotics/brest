class Observable:
    def __init__(self, initial_value=None):
        self.data = initial_value
        self._callbacks = []

    def add_callback(self, callback):
        """
        Subsribe to value change

        :param callback: method to call on event
        """
        self._callbacks.append(callback)

    def del_callback(self, callback):
        """
        Unsubscribe for a value change

        :param callback: method to call on event
        """
        self._callbacks.remove(callback)

    def _do_callbacks(self):
        """
        Trigger every subscribed function
        """
        for func in self._callbacks:
            func(self.data)

    def set(self, data):
        """
        Update data

        :param data: value to set
        """
        self._data = data
        self._do_callbacks()

    def get(self):
        """
        Get data
        """
        return self._data



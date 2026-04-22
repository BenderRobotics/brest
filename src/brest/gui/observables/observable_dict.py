from brest.gui.observables import Observable


class ObservableDict(dict, Observable):
    """
    Wrapper introducing notification for dict changes
    on event appropriate callbacks are triggered for ever key: value

    valid events:
        'on_create' - triggered on new key creation
        'on_delete' - triggered on delete of key
        'on_change' - triggered on value change
        'on_update' - triggered in all cases above

    :param initial: dict
    """
    def __init__(self, initial_value={}, **kwargs):
        Observable.__init__(self, **kwargs)
        dict.__init__(self, **kwargs)

        dict.update(self, initial_value)

        self._callbacks = {
            'on_create': [],
            'on_update': [],
            'on_delete': [],
            'on_change': [],
        }

    def add_callback(self, event, callback):
        """
        Add callback for specific event

        :param event: name of event, can be passed as tupple
        :param callback: function to call
        """
        if isinstance(event, tuple):
            for e in event:
                self._callbacks[e].append(callback)
        else:
            self._callbacks[event].append(callback)

    def del_callback(self, event, callback):
        """
        Delete callback for specific event

        :param event: name of event, can be passed as tuple
        :param callback: function to call
        """
        if isinstance(event, tuple):
            for e in event:
                self._callbacks[e].remove(callback)
        else:
            self._callbacks[event].remove(callback)

    def _do_callbacks(self, new, event):
        if isinstance(event, str):
            event = [event]

        for e in event:
            for func in self._callbacks[e]:
                func(new, e)

    def __setitem__(self, key, value):
        event = "on_update"

        if key not in self:
            event = "on_create"

        dict.__setitem__(self, key, value)
        self._do_callbacks({key: value}, (event, "on_update"))

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._do_callbacks({key: None}, ("on_delete", "on_update"))

    def update(self, *args, **kwargs):
        before = set(self.items())

        dict.update(self, *args, **kwargs)

        after = set(self.items())

        # * Find out which items changed or were created and make callback
        updated_keys = []
        for update in (before - after):
            self._do_callbacks({update[0]: update[1]}, ("on_change", "on_update"))
            updated_keys.append(update[0])

        for create in (after - before):
            if create[0] not in updated_keys:
                self._do_callbacks({create[0]: create[1]}, ("on_create", "on_update"))
            else:
                updated_keys.remove(create[0])

    def pop(self, key, **kwargs):
        dict.pop(key, **kwargs)
        self._do_callbacks({key: None}, ("on_delete", "on_update"))

    def list_callbacks(self):
        """
        List all registered callbacks

        :returns: dict with registered callbacks for every event type
        """
        return self._callbacks

    def trigger_on_all(self, event):
        """
        Trigger event on every item

        :param event: event to trigger
        """
        [self._do_callbacks({key: value}, event) for key, value in self.items()]

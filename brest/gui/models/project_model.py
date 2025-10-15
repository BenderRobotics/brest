from brest.gui.observables import ObservableDict


class ProjectModel:
    """
    Introduce buffer for changes, triggers file write on save

    """

    DEFAULT_NEW_NAME = "res {}"

    def __init__(self, name, content):
        self.content = content
        self.name = name

    def _get_name(self):
        i = 0
        while True:
            new_name = self.DEFAULT_NEW_NAME.format(i)
            if new_name not in self.content:
                return new_name
            i += 1

    def add_resource(self):
        new_name = self._get_name()
        self.content[new_name] = ObservableDict()
        return new_name

    def del_resource(self):
        pass

    def update_resource(self):
        pass

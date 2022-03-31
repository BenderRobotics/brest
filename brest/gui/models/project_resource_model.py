class ProjectResourceModel:
    """
    Holds data for specific resource, propagate changes to PorjectModel
    """
    def __init__(self, name, params=None):
        self.params = params
        self.defaults = {}  # todo get default and available values from brest
        self.name = name

    def add_param(self, item, value=None):
        """
        Add parameter to a model, if value is None value is taken from defaults,
        if there is no record in defaults ValueError is raised
        """
        if value is None:
            if item in self.defaults:
                value = self.defaults[item]
            else:
                raise ValueError("No value to set!")

        self.params[item] = value

    def del_param(self, item):
        pass

    def add_default(self, item, value):
        pass

    def update_defaults(self, defaults):
        pass

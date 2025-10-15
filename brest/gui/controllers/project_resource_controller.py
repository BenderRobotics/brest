from brest.gui.views import ProjectResourceView
from brest.gui.models import ProjectResourceModel


class ProjectResourceController:
    def __init__(self, master, name, params):
        self.view = ProjectResourceView(master, name, params)
        self.model = ProjectResourceModel(name, params)

        # todo get default params
        # todo add defaults to model

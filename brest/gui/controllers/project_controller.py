from brest.gui.models import ProjectModel
from brest.gui.views import ProjectView
from .project_resource_controller import ProjectResourceController


class ProjectController:
    # name can be obtained from model
    def __init__(self, master, name, content):
        self.master = master

        self.model = ProjectModel(name, content)
        self.view = ProjectView(master)

        # ! change to function get_name()
        self.name = self.model.name

        self.resources = []

        self.model.content.add_callback("on_create", self._on_new_resource)
        #self.model.content.add_callback("on_change", self.view.update_resource)
        #self.model.content.add_callback("on_delete", self.view.del_resource)

        self.model.content.trigger_on_all("on_create")

    def add_resource(self, item, value):
        """
        Add resource request from user control
        """

        # * Crete record in model and get name
        self.model.add_resource()


    def _on_new_resource(self, item, event):
        """
        Creates resource controller for new record of resource
        """
        for resource_name, content in item.items():
            # * Pass name and record to resource controller
            self.resources.append(
                ProjectResourceController(
                    self.view.scrollable_frame.scrollable_frame,
                    resource_name,
                    content
                )
            )

    def del_resource(self):
        pass

    def save_config(self):
        pass

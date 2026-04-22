from brest.gui.views import ConfigView
from brest.gui.controllers import ProjectController
from brest.gui.models import ConfigModel
from brest.config import Config

from tkinter import filedialog


class ConfigController:
    def __init__(self, master):
        self.master = master

        self.view = ConfigView(master)
        self.model = ConfigModel()

        self.view.add_resource_button.config(command=self.add_resource)
        self.view.create_resource_button.config(command=self.add_resource)

        self.tabs = []

    def _get_selected_tab(self):
        selected_tab = self.view.get_selected_view()
        for tab in self.tabs:
            if selected_tab == tab.view:
                return tab

    def add_tab(self, file_path, project_name):
        project_content = self.model.get_project_content(file_path, project_name)

        self.tabs.append(ProjectController(self.view.notebook, project_name, project_content))
        self.view.add_tab(self.tabs[-1].view, self.tabs[-1].name)

    def open_user_config(self):

        file_path = Config.BREST_USER_CONFIG
        file = self.model.open_file(file_path)
        if not file:
            file_path = filedialog.askopenfilename(
                defaultextension=".yaml",
                filetypes=[("Yaml", "*.yaml")]
            )
            self.model.open_file(file_path)

        # * Create tab for every project
        [self.add_tab(file_path, project) for project in self.model.get_projects(file_path)]

    def add_resource(self, params=None):
        tab = self._get_selected_tab()

        tab.add_resource(params)

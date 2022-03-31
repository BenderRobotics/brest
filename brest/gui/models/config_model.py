import yaml
import logging

from yaml.parser import ParserError
from yaml.scanner import ScannerError

from brest.gui.observables import ObservableDict


class ConfigModel:
    """
    Handling of all file streams
    """
    def __init__(self):
        self._opened_files = {}
        self.logger = logging.getLogger()

    def _parse(self, content):
        try:
            serialized_content = yaml.load(content, Loader=yaml.Loader)
            if not serialized_content:
                serialized_content = {}
        except (ParserError, ScannerError) as ex:
            self.logger.error('Error during config parsing:\n{}'.format(ex))
            return None
        return serialized_content

    def _get_file_handle(self, path):
        """
        Return file handle

        :param path: path to a file
        :returns: file handle
        """
        return self._opened_files[path]['handle']

    def _get_buffer(self, path):
        """
        Returns file buffer

        :param path: path to a file
        :returns: file buffer
        """
        return self._opened_files[path]['buffer']

    def open_file(self, path):
        """
        Open file parse it and create buffer for it, returns its content
        if file is already opened returns its content

        :param path: path to a file
        :returns: serialized content of file
        """
        if path in self._opened_files:
            return self.get_file(path)

        try:
            file_handle = open(path, "r+")
            content = file_handle.read()
        except OSError as ex:
            self.logger.error("Could not open file.\n{}".format(ex))
            return None

        content = self._parse(content)

        # * Create observable structure
        buffer = {}
        for project, resources in content.items():
            buffer[project] = ObservableDict()
            for resource, params in resources.items():
                buffer[project][resource] = ObservableDict(params)

        self._opened_files.update({path: {
            'handle': file_handle,
            'buffer': buffer,
        }})

        return self._opened_files[path]

    def save_file(self, path):
        """
        Dumps buffered content to opened file

        :param path: path to a file
        """
        handle = self._get_file_handle(path)
        handle.seek(0)
        yaml.dump(self._get_buffer(path), handle)
        handle.truncate()

    def close_file(self, path):
        """
        Close opened file

        :param path: path to a file
        """
        handle = self._get_file_handle(path)
        handle.close()
        del self._opened_files[path]

    def get_file(self, path):
        """
        Return serialized data of opened file

        :param path: path to a file
        :returns: dict
        """
        content = self.get_file_raw(path)
        return self._parse(content)

    def get_file_raw(self, path):
        """
        Return raw file data of opened file

        :param path: path to a file
        :returns: string
        """
        if path not in self._opened_files:
            raise ValueError("Unknown file")
        handle = self._get_file_handle(path)
        handle.seek(0)
        return handle.read()

    def get_projects(self, path):
        """
        Return list of projects for opened file

        :param path: path to a file
        :returns: list with names of projects
        """
        return [key for key in self._get_buffer(path)]

    def get_project_content(self, path, project):
        """
        Return contents of given project

        :param path: path to a file
        :param project: project name
        :returns: serialized contents of project
        """
        return self._get_buffer(path)[project]

    def update_project(self, path, project, content):
        """
        Update buffered contents of project

        :param path: path to file
        :param project: project name
        """
        self._opened_files[path]['buffer'][project].update(content)

    def add_project(self, path, project):
        """
        Add project to buffered contents

        :param path: path to file
        :param project: project name
        """
        self._opened_files[path]['buffer'][project] = {}

    def del_project(self, path, project):
        """
        Del project from buffered contents

        :param path: path to file
        :param project: project name
        """
        del self._opened_files[path]['buffer'][project]

    def close_all(self):
        """
        Close all opened files
        """
        for path, value in self._opened_files.items():
            value['handle'].close()

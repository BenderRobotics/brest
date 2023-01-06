#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.cli_communicable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base functionality for communicating with a cli utility.

    :copyright: 2023 Bender Robotics
"""

import sys
import os.path
import logging
import subprocess

from brest.communication import Communicable
from brest.communication import CommunicationStructure
from brest.communication.types import str_t

class CLICommunicable(Communicable):
    """
    Base class for providing communication with a cli utility.

    This shouldn\'t be used as a Communicable base for a resource. Derive
    from this class and implement :meth:`~brest.Communication.probe`,
    :meth:`~brest.Communication.mark_taken`, :meth:`~brest.Communication.is_taken`,
    :meth:`~brest.Communication.get_available`, :meth:`~brest.Communication.format_interface`
    to provide full functionality for Brest.
    This class provides you two methods for communication with the cli utility
    use :meth:`~brest.communication.CLICommunicable.write_raw` to run cli utility with given
    args and :meth:`~brest.communication.CLICommunicable.read_raw` to get the return code and
    output of the utility. Then for example, you could implement
    :meth:`~brest.communication.Communicable.transcieve` to accept a custom command, which will
    be transformed into the args for the cli utility and then parse the string output to response
    message.

    :param params: Construction parameters
    :type  params: dict
    """

    TYPE = 'cli'
    TAKEN = []
    SETTINGS = ['cli_path']

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self._cli_subprocess = None

        #: Encoding of the cli utility output
        #: Default values are ``cp1251`` for win32 or ``utf-8`` otherwise
        self.ENCODING = 'cp1252' if sys.platform == 'win32' else 'utf-8'

        if params:
            self.cli_path = params.get('cli_path')
            self.check_connection()

    @property
    def cli_subprocess(self):
        """
        Returns reference to the :class:`subprocess.Popen` subprocess used for the communication
        with the cli utility.
        """

        return self._cli_subprocess

    def check_connection(self):
        """
        Checks if cli exists and is runnable.

        :raises ValueError: In case of ``cli_path`` not being executable
        :raises FileNotFoundError: In case of incorrect ``cli_path``
        """

        if not hasattr(self, 'cli_path') or not self.cli_path:
            raise ValueError('Missing path to the cli utility')
        try:
            if not os.access(self.cli_path, os.X_OK):
                raise ValueError('Specified cli path is not executable')
        except FileNotFoundError:
            raise FileNotFoundError('Specified cli path doesn\'t exist')

    def write_raw(self, cli_args):
        """
        Executes the cli with given params.

        :param cli_args: Arguments for cli utility. This must be a list of strings.
                         Each string will be concat using space as you would normally
                         do when using a cli utility.
        :type  cli_args: list of str
        """

        if not isinstance(cli_args, list):
            raise ValueError('cli_args must be a list')
        self._cli_subprocess = subprocess.Popen([self.cli_path] + cli_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def read_raw(self):
        """
        Reads from the subprocess stdout in which was cli utility called.

        :returns: Return code and output from subprocess running cli utility in a tuple
        :rtype: tuple
        """

        return (self._cli_subprocess.returncode, self._cli_subprocess.stdout.read().decode(self.ENCODING))

    def get_connections(self):
        return []

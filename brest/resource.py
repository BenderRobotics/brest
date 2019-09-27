# -*- coding: utf-8 -*-
"""
    brest.resource
    ~~~~~~~~~~~~~~

    This module implements base attributes and method for resource.

    :copyright: 2019 Bender Robotics
"""

import logging

class Resource():
    """Base class for representing resource by name."""

    _count = 0

    def __init__(self):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.name = 'resource_' + str(Resource._count)
        Resource._count += 1

    def check_required(self, requirements):
        for name, value in requirements.items():
            name = 'required_' + name
            req_func = getattr(self, name, None)
            if not req_func:
                # self.logger.error('Missing requirement check function `{}`'.format(name), extra=self.log_args)
                return False
            if not req_func(value):
                # self.logger.error('Resource doest satisfy `{}` requirement check', extra=self.log_args)
                return False
        return True

    def set_default(self, defaults):
        for name, value in defaults.items():
            name = 'default_' + name
            def_func = getattr(self, name, None)
            if not def_func:
                return False
            if not def_func(value):
                return False
        return True

    def set_extra(self, params):
        for name, value in params.items():
            if hasattr(self, name):
                setattr(self, name, value)

    def _parse_args(self, kwargs):
        """If object has attribute specified in `kwargs` dict, sets its value.

        :param kwargs: A dictionary indexed by attribute names which contains attribute values from configuration file.
        :type  kwargs: dict
        """

        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                if attr != 'interface':
                    self.logger.warning('Class `{}` don\'t have `{}` attribute'.format(self.__class__.__name__, attr), extra=self.log_args)

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

    def __init__(self, params):
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        if params and 'name' in params:
            self.name = params['name']
        else:
            self.name = 'resource_' + str(Resource._count)
            Resource._count += 1

    def check_required(self, requirements):
        for name, value in requirements.items():
            name = 'required_' + name
            req_func = getattr(self, name, None)
            if not req_func:
                self.logger.error('`{}` is missing requirement check function `{}`'.format(self.name, name), extra=self.log_args)
                return False
            if not req_func(value):
                return False
        return True

    def set_default(self, defaults):
        for name, value in defaults.items():
            name = 'default_' + name
            def_func = getattr(self, name, None)
            if not def_func:
                self.logger.error('`{}` is missing function `{}` to set default value'.format(self.name, name), extra=self.log_args)
                return False
            if not def_func(value):
                return False
        return True

    def set_aliases(self, aliases):
        ali_func = getattr(self, 'aliases', None)
        if not ali_func:
            self.logger.error('`{}` is missing `aliases` function to set aliases'.format(self.name), extra=self.log_args)
            return False
        if not ali_func(aliases):
            return False
        return True

    def set_extra(self, params):
        for name, value in params.items():
            if hasattr(self, name):
                setattr(self, name, value)

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

# -*- coding: utf-8 -*-
"""
    brest
    ~~~~~

    Bender Robotics Embedded System Tool for resource managing.

    :copyright: 2019 Bender Robotics
"""

# Set up brest logging facility
import logging.config
from .log import DEFAULT_LOGGING

logging.config.dictConfig(DEFAULT_LOGGING)

from .log import CharStreamHandler
from .config import Config
from .resource import Resource
from .resources import Resources
from .resource_provider import ResourceProvider
from .log import FilterAvailable
from .helpers import overwrite_log_config, prepare_tests

__all__ = [
    'CharStreamHandler',
    'Config',
    'Resource',
    'Resources',
    'ResourceProvider',
    'FilterAvailable',
    'overwrite_log_config',
    'prepare_tests',
    'create_subprocess',
    'replace_log_handler',
    ]

__version__ = '0.0.1'

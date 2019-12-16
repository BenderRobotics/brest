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

# Add hex representer
from yaml import add_representer
from .helpers import HexInt, hex_representer
add_representer(HexInt, hex_representer)

from .log import CharStreamHandler
from .config import Config
from .resource import Resource
from .resources import Resources
from .resource_provider import ResourceProvider
from .log import FilterAvailable
from .helpers import overwrite_log_config, prepare_tests
from .log_subprocess import run

__all__ = [
    'CharStreamHandler',
    'Config',
    'Resource',
    'Resources',
    'ResourceProvider',
    'FilterAvailable',
    'HexInt',
    'overwrite_log_config',
    'prepare_tests',
    'create_subprocess',
    'replace_log_handler',
    'run',
    ]

__version__ = '0.0.4'

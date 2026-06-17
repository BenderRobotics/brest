#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.__init__
    ~~~~~~~~~~~~~~

    This file signifies that 'brest' is a module.

    Brest is package for handling of peripherals.
    It aims at making embedded development and testing easier,
    mainly by reducing the time needed to set up the HW.

    :copyright: 2024 Bender Robotics
"""

# Verify Python version
import sys
supported_versions = (
    '\r\n\t3.5+'
)
if sys.version_info.major != 3 or sys.version_info.minor < 5:
    print('\r\n============================================================')
    print('ERROR (brest): Python version (%d.%d) invalid, exiting!' % (sys.version_info.major, sys.version_info.minor))
    print('INFO  (brest): Supported Python versions:%s' % supported_versions)
    print('============================================================\r\n')
    sys.exit()

# Set up brest logging facility
import logging
import logging.config
from .log import DEFAULT_LOGGING

logging.config.dictConfig(DEFAULT_LOGGING)

# Add hex representer
from yaml import add_representer
from .helpers import HexInt, hex_representer
add_representer(HexInt, hex_representer)

from .__version__ import __version__
from .log import CharStreamHandler
from .config import Config
from .resource import Resource
from .resources import Resources
from .resource_provider import ResourceProvider, _ResourceProvider
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
    'find_available_resource',
    'print_available',
    'print_taken',
    'print_all',
    'generate_config',
    'run',
]


def find_available_resource(projects, resource, user_config=Config.BREST_USER_CONFIG, project_config=None):
    """
    Tries to find descriptors of connected device that matches resource from given project.

    :param projects: List of selected projects that Brest will look for in your config files.
    :type projects: str, list
    :param resource: Selected resource to be found.
    :type resource: str
    :param user_config: An absolute path to user configuration file in non standard location
    :type user_config: str
    :param project_config: Optional project config to be merged with default user config.
    :type project_config: str
    :return: `dict` representing selected resource or `None` if resource not found.
    :rtype: dict
    """
    logger = logging.getLogger('brest_find_available_resource')
    logger.setLevel(logging.INFO)
    rp = _ResourceProvider()

    config_file = Config(projects, project_config)
    merged_configs = config_file.merge_configs(Config(projects, user_config))

    if not merged_configs.is_valid:
        logger.warning(
            "Set `project`/`projects` is not found in config file created from user_config and project_config."
        )
        return None

    if resource not in merged_configs.config:
        logger.warning(f"Set {resource} is not found in config file created from user_config and project_config.")
        return None

    resource_needed = merged_configs.config[resource]
    class_name_split = resource_needed['class_name'].split('.')

    if len(class_name_split) > 1:
        needed_class_name = class_name_split[1]
        implicit_interface = rp._get_implicit_definition(needed_class_name)
        implicit_communicable = rp._get_communicable(implicit_interface['type'])

        interface_needed = implicit_interface
        try:
            interface_needed.update(resource_needed['interface'])
        except:
            pass
        intr = implicit_communicable.probe(interface_needed)
        if intr:
            # precaution against non-existent 'interface' key in 'resource_needed'
            temp_dict = {}
            temp_dict['interface'] = intr[0]
            # update the interface
            resource_needed.update(temp_dict)
            return resource_needed
    else:
        logger.warning(
            f"The device class name {resource_needed['class_name']} in the created config file "
            "is not specific enough to find descriptors of connected device. "
            f"Consider extending `class_name` of the resource {resource} "
            "(e.g. `Supplies.Tenma` instead of plain `Supplies`)."
        )

    return None

def print_available(group=None):
    """
    Tries to find available resources.

    :param group: Specified group of resources to be printed. To get available groups refer to the :ref:`supported`
    :type group: str
    """
    rp = _ResourceProvider()

    def print_av_dict(available_dict):
        print(' | '.join([c.split(',')[-1] for c in available_dict['class_name']]))
        com = rp._get_communicable(available_dict['interface']['type'])
        for attr in com.format_interface(available_dict['interface']):
            print('\t{}: {}'.format(attr[0], attr[1]))

    if group:
        av = rp.available(group)
    else:
        av = rp.available()

    i = 0
    for a in av:
        print('[{}] '.format(i), end='')
        print_av_dict(a)
        print()
        i += 1

def print_taken():
    """
    Prints taken resources.
    """
    rp = _ResourceProvider()
    taken = rp.get_taken()

    for item in taken:
        print(item['resource'])
        for key, value in item['interface'].items():
            print(f'\t{key}: {value}')
        print()

def print_all():
    """
    Prints taken and available resources.
    """
    rp = _ResourceProvider()
    
    # Get taken and available resources
    taken = rp.get_taken()
    av = rp.available()

    def print_av_dict(available_dict):
        print(' | '.join([c.split(',')[-1] for c in available_dict['class_name']]))
        com = rp._get_communicable(available_dict['interface']['type'])
        for attr in com.format_interface(available_dict['interface']):
            print('\t{}: {}'.format(attr[0], attr[1]))

    print('--Taken resources--------------------')
    for item in taken:
        print(item['resource'])
        for key, value in item['interface'].items():
            print(f'\t{key}: {value}')
        print()

    print('--Available resources----------------')
    i = 0
    for a in av:
        print('[{}] '.format(i), end='')
        print_av_dict(a)
        print()
        i += 1

def generate_config(project_name='autogen', config_path=Config.BREST_USER_CONFIG):
    """
    Autogenerates configuration file from available resources.

    Lists currently available resources and make a basic configuration file containing
    filled interfaces for these resources. Default configuration path is
    :attr:`~brest.Config.BREST_USER_CONFIG` and default project name is \'autogen\'.
    If the file already exist, project will be appended to the end of file. In case
    of existing project with same name, the project will be overwritten.

    :param project_name: Name of the generated project
    :type  project_name: str
    :param config_path: Absolute path
    :type  config_path: str
    :returns: Generated configuration object
    :rtype: :class:`~brest.Config`
    """
    rp = _ResourceProvider()
    available = rp.available()
    project_dict = dict()
    i = 0

    for av in available:
        for class_name in av['class_name']:
            alias = 'resource_' + str(i)
            project_dict[alias] = {
                'class_name': class_name,
                'interface': dict(av['interface'])
            }
            com = rp._get_communicable(av['interface']['type'])
            for attr in com.format_interface(av['interface']):
                project_dict[alias]['interface'][attr[0]] = attr[1]
            i += 1

    config = Config(config_path=config_path)
    project_configs = []
    project_found = False

    for project in config.read_projects():
        project_config = Config(project, config_path=config_path)

        if project == project_name:
            project_config = project_config.merge_configs(
                Config(project_name, config_dict={project_name: project_dict})
            )
            project_found = True

        project_configs.append(project_config)

    if not project_found:
        project_configs.append(Config(project_name, config_dict={project_name: project_dict}))

    config.clear_yaml(config_path)
    for project_config in project_configs:
        project_config.dump_yaml(config_path)
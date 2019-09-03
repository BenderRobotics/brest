# Set up brest logging facility
import brest.log
import logging.config

logging.config.dictConfig(log.DEFAULT_LOGGING)

from .config import Config
from .resource import Resource
from .resource_provider import ResourceProvider

__all__ = [
    'Config',
    'Resource',
    'Resources',
    'ResourceProvider',
    'overwrite_log_config',
    'prepare_tests',
    ]

class Resources():
    '''
    Top level class for resource managing
    '''

    def __init__(self, project, config = Config.BREST_CONFIG, needed = []):
        self.log_args = {'class_name':self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.resources = {}
        self.instantiate(project, config, needed)

    def __str__(self):
        if not self.resources:
            return str(self.__class__)
            
        just = max([len(k) for k in self.resources.keys()]) + 1
        s = '%s: {\n    ' % self.__class__.__name__
        s += '\n    '.join(['%s: %s' % (str(k).ljust(just), str(self.resources[k])) for k in sorted(self.resources)])
        s += "\n}"
        return s

    def __getitem__(self, key):
        if key in self.resources:
            return self.resources[key]
        else:
            raise KeyError(f'Invalid key: {key}')

    def __iter__(self):
        return iter(self.resources.items())

    def instantiate(self, project, config, needed):
        cfg = Config(project)
        cfg.needed = needed
        if not cfg.is_valid:
            self.logger.error('Configuration file is not valid', extra=self.log_args)
            raise SystemExit

        rp = ResourceProvider()

        res = []
        res.extend(rp.construct_config(cfg))

        for r in res:
            # Failed object construction results in None being in the list
            if r:
                self.resources[r.name] = r
            else:
                self.logger.error('Could\'t initialize all resources', extra=self.log_args)
                raise SystemExit        
        
        if self.resources:
            self.logger.info(f'All resources successfully initialized\n{str(self)}', extra=self.log_args)
        else:
            self.logger.warning('No resources were initialized', extra=self.log_args)

def overwrite_log_config(config_dict):
    '''
    Method takes a logging configuration dictionary and merges it with the brest implicit configuration.
    '''

    custom_config = dict(log.DEFAULT_LOGGING)
    for ov_key, ov_value in config_dict.items():
        __apply_overwrite(custom_config, ov_key, ov_value)
    logging.config.dictConfig(custom_config)

def __apply_overwrite(node, key, value):
    if isinstance(value, dict):
        for item in value:
            if key in node:
                __apply_overwrite(node[key], item, value[item])
            else:
                node[key] = value
    else:
        node[key] = value

def prepare_tests(test_suite, project, config=Config.BREST_CONFIG):
    '''
    Method takes test_suite object created using unittest.discover(). It collects
    all needed resources from test, construct them and sets as class a attribute on
    every test.
    Returns Resources instance
    '''

    # collect needed resources
    needed = []
    for folder_suite in test_suite:
        for file_suite in folder_suite:
            for test in file_suite:
                for n in test.needed:
                    if n not in needed:
                        needed.append(n)

    # construct them
    resources = brest.Resources(project, config=config, needed=needed)

    # set constructed resources to every test
    for folder_suite in test_suite:
        for file_suite in folder_suite:
            for test in file_suite:
                test.resources = resources

    return resources
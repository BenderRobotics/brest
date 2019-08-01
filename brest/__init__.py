from .config import Config
from .resource import Resource
from .resource_provider import ResourceProvider

__all__ = ['Config', 'Resource', 'Resources', 'ResourceProvider']

class Resources():
    '''
    Top level class for resource managing
    '''

    def __init__(self, project, alt_config = None):
        self.log_args = {'class_name':self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')
        self.resources = {}
        self.instantiate(project, alt_config)
        self.list_initialized()

    def __str__(self):
        just = max([len(k) for k in self.resources.keys()]) + 1
        s = '%s: {\n    ' % self.__class__.__name__
        s += '\n    '.join(['%s: %s' % (str(k).ljust(just), str(self.resources[k])) for k in sorted(self.resources)])
        s += "\n}"
        return s

    def __getitem__(self, key):
        if key in self.resources:
            return self.resources[key]
        else:
            raise KeyError("Invalid key: {}".format(key))

    def __iter__(self):
        return iter(self.resources.items())

    def instantiate(self, project, alt_config):
        if alt_config:
            cfg = Config(project, alt_config)
        else:
            cfg = Config(project)
        if not cfg.is_valid:
            return

        rp = ResourceProvider()

        res = []
        res.extend(rp.construct_config(cfg))

        for r in res:
            # Failed object construction results in None being in the list
            if r:
                self.resources[r.name] = r

    def list_initialized(self):
        if self.resources:
            self.logger.info(f'Listing successfully initialized resources', extra=self.log_args)
            for alias, cls_ in self.resources.items():
                self.logger.info(f'`{alias}` of class {cls_.__class__.__module__ + "." + cls_.__class__.__name__}', extra=self.log_args)
        else:
            self.logger.warning(f'Didn\'t initialize any resource', extra=self.log_args)

# Set up brest logging facility
import yaml
import brest.log
import logging.config

with open('log_config.yaml') as stream:
    logging_cfg = yaml.load(stream, Loader=yaml.SafeLoader)
logging.config.dictConfig(logging_cfg)
del logging_cfg
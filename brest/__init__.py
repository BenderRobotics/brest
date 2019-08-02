from .config import Config
from .resource import Resource
from .resource_provider import ResourceProvider

__all__ = ['Config', 'Resource', 'Resources', 'ResourceProvider']

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

    def instantiate(self, project, config, needed):
        cfg = Config(project)
        cfg.needed = needed
        if not cfg.is_valid:
            self.logger.error('Can\'t construct any resource. Configure file is not valid')
            return

        rp = ResourceProvider()

        res = []
        res.extend(rp.construct_config(cfg))

        for r in res:
            # Failed object construction results in None being in the list
            if r:
                self.resources[r.name] = r
            else:
                self.logger.error('All resources could\'t be initialized', extra=self.log_args)
                raise SystemExit        
        
        self.logger.info(f'All resources successfully initialized\n{str(self)}', extra=self.log_args)

# Set up brest logging facility
import yaml
import brest.log
import logging.config

with open('log_config.yaml') as stream:
    logging_cfg = yaml.load(stream, Loader=yaml.SafeLoader)
logging.config.dictConfig(logging_cfg)
del logging_cfg
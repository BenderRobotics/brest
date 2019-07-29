from .config import Config
from .resource import Resource
from .resource_provider import ResourceProvider

__all__ = ['Config', 'Resource', 'Resources', 'ResourceProvider']

class Resources():
    '''
    Top level class for resource managing
    '''

    def __init__(self, project, config_path = None):
        self.resources = {}
        self.instantiate(project)

    def __getitem__(self, key):
        if key in self.resources:
            return self.resources[key]
        else:
            raise KeyError("Invalid key: {}".format(key))

    def __iter__(self):
        return iter(self.resources.items())

    def instantiate(self, project):
        cfg = Config(project)
        rp = ResourceProvider()

        res = []
        res.extend(rp.construct_config(cfg))

        for r in res:
            # Failed object construction results in None being in the list
            if r:
                self.resources[r.name] = r 
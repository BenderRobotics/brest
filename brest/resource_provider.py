import importlib

class ResourceProvider:
    '''
    Base class for specific resource providers.
    '''

    @staticmethod
    def probe(resource, known_params = None):
        '''
        Checks if resource is present in the system, and returns its port's name.
        '''

        raise NotImplementedError('This provider does not support resource probing.')

    @staticmethod
    def available():
        '''
        Searches for all available resources present in the system.
        '''

        raise NotImplementedError('This provider does not support available resource listing.')

    @staticmethod
    def construct(kwargs):
        '''
        Constructs a resource from given parameters.
        '''

        raise NotImplementedError('This provider does not support resource instantiation .')

    @staticmethod
    def construct_config(config):
        '''
        Constructs all available resources described in config.
        '''

        raise NotImplementedError('This provider does not support all available resource in config instantiation .')

    @staticmethod
    def _construct(module_name, kwargs):
        '''
        Generic method for class instantiation from given module.
        '''

        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, kwargs['class_name'])
            del kwargs['class_name']
            return class_(kwargs)
        except:
            #TODO: Notice user about brest not being able to construct given class
            return None
import importlib

class ResourceProvider:
    '''
    '''

    @staticmethod
    def probe(resource):
        raise NotImplementedError('This provider does not support resource probing.')

    @staticmethod
    def available():
        raise NotImplementedError('This provider does not support available resource listing.')

    @staticmethod
    def construct(**kwargs):
        raise NotImplementedError('This provider does not support resource instantiation .')

    @staticmethod
    def construct_available():
        raise NotImplementedError('This provider does not support all available resource instantiation .')

    @staticmethod
    def _construct(module_name, **kwargs):
        from brest.supplies import __all__ as classes
        if kwargs['name'] in classes:
            module = importlib.import_module(module_name)
            class_ = getattr(module, kwargs['name'])
            del kwargs['name']
            return class_(**kwargs)
        return None
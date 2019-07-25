from brest import Resource

class Loads(Resource):
    
    KNOWN = {
        'PLI' : {'vid' : 0x0403, 'pid' : 0x06001, 'serial' : 'FT99QOL2A'}
    }

    def __init__(self):
        self._current = 0
        self.MAX_CURRENT = None

    def enable(self):
        raise NotImplementedError('This load cannot be enabled.')

    def disable(self):
        raise NotImplementedError('This load cannot be disabled.')

    @property
    def current(self):
        raise NotImplementedError('This load is unable to measure output current.')

    @current.setter
    def current(self):
        raise NotImplementedError('This load does not support different current limits.')

    def get_info(self):
        raise NotImplementedError('This load has no means of status detection.')

    def clear(self):
        raise NotImplementedError('This load does not support registers clear.')

    def reset(self):
        raise NotImplementedError('This load does not support reset to default values.')

    def self_test(self):
        raise NotImplementedError('This load does not support sefl testing.')
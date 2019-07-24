class Resource():
    '''
    Base class for representing resource by name
    '''

    cnt = 0

    def __init__(self, kwargs):
        super().__init__(kwargs)
        self.name = 'resource_' + str(Resource.cnt)
        Resource.cnt += 1

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def parse_args(self, kwargs):
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                print('u tridy {} nastavuji {} na {}'.format(self.__class__, attr, value))
                setattr(self, attr, value)
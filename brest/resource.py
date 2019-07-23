class Resource():
    '''
    Base class for representing resource by name
    '''

    cnt = 0

    def __init__(self, name = None):
        if name is None:
            self.name = 'resource_' + str(Resource.cnt)
            Resource.cnt += 1
        else:
            self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
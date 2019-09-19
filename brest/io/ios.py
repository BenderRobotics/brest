from brest import Resource

class IO(Resource):

    KNOWN = {}

    def __init__(self):
        Resource.__init__(self)
        self._states = 0
        self.IDN = None
        self.CHANNELS = 0
        self.MAX_CURRENT = None
        self.IS_LATCHING = None

    def __getitem__(self, key):
        if isinstance(key, slice):
            ret = []
            for i in self.__parse_slice(key):
                ret.append(True if (0x1 << i) & self._states else False)
            return ret

        return True if (0x1 << key) & self._states else False

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            for i in self.__parse_slice(key):
                self[i] = value
            return

        if value:
            self._states |= (0x1 << key)
        else:
            self._states &= ~(0x1 << key)

    def get_states(self):

        raise NotImplementedError()

    def set_states(self):

        raise NotImplementedError()

    def __parse_slice(self, slice_):
        start = slice_.start if slice_.start else 0
        stop  = slice_.stop + 1  if slice_.stop  else self.CHANNELS
        step  = slice_.step  if slice_.step  else 1
        return range(start, stop, step)
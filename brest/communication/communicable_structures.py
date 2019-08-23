import logging

class Packable():
    '''
    Base class for structures, that can be serialized into and deserialized from a bytearry.
    '''

    def __init__(self):
        self.byteorder = '>'

    def pack(self, data, offset):
        raise NotImplementedError('This structure can\'t be packed')

    def unpack(self, data, offset):
        raise NotImplementedError('This structure can\'t be unpacked')

    def is_padded(self, data, offset):
        return offset // 8 == len(data) and (offset % 8 == 0 or offset % 8 == 8)

    def pad_size(self, offset):
        pad = 8 - (offset % 8)
        return pad if pad != 8 else 0

class CommunicationStructure(Packable):
    '''
    Base class for message creation.
    '''

    def __init__(self, byteorder = '>'):
        Packable.__init__(self)
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.raw_data = bytearray()
        self.byteorder = byteorder
        self.packable = []
        self.packable_full = []    
        self.full = True
        self.value_ = self

    def __eq__(self, other):
        for pair in zip(self.get_packable_attributes(True), other.get_packable_attributes(True)):
            if pair[0].value_ != pair[1].value_:
                return False
        return True

    def add(self, name, value, full_only = False):
        '''
        Adds packable type as an atribute. Name can\'t be `value_` which is reserved for internal values.
        '''

        if name == 'value_':
            self.logger.error('Name can\'t be `value_` which is reserved for internal values', extra=self.log_args)
            raise SystemExit

        if not issubclass(value.__class__, Packable):
            self.logger.error(f'Value in `{name}` must derive from Packable class', extra=self.log_args)
            raise SystemExit

        internal_name = '_' + name
        value.byteorder = self.byteorder           # set message specific byteorder
        setattr(self, internal_name, value)        # create attribute  
        setattr(self.__class__, name, property(
            lambda self: getattr(self, internal_name).value_,                           # create getter
            lambda self, value: setattr(getattr(self, internal_name), 'value_', value)) # create setter
        )
        self.packable_full.append(name) if full_only else self.packable.append(name)

    def get_packable_attributes(self, full):
        attrs = []
        for attr_name in self.packable:
            attrs.append(getattr(self, '_' + attr_name))
        if full:
            for attr_name in self.packable_full:
                attrs.append(getattr(self, '_' + attr_name))
        return attrs

    def pack(self, data = None, offset = 0):
        if data == None:
            self.raw_data = bytearray()
            data = self.raw_data

        for attr in self.get_packable_attributes(self.full):
            offset = attr.pack(data, offset)

        return offset

    def unpack(self, data = None, offset = 0):
        if data == None:
            data = self.raw_data

        for attr in self.get_packable_attributes(True):
            offset = attr.unpack(data, offset)

        return offset
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
        self.lengths_ = {}

    def __eq__(self, other):
        for pair in zip(self.get_packable_attributes(True), other.get_packable_attributes(True)):
            if pair[0].value_ != pair[1].value_:
                return False
        return True

    def add(self, name, value, full_only = False, attr_len = None):
        '''
        Adds packable type as an atribute. Name cant\'t be `value_` or `lengths_` which are reserved for internal values.
        If attr_len is specified, value is treated as a length for another atribute.
        '''

        if name in ['value_', 'lengths_']:
            self.logger.error(f'Name can\'t be `{name}` which is reserved for internal values', extra=self.log_args)
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

        if attr_len:
            self.lengths_[name] = attr_len

    def change(self, name, new_value):
        internal_name = '_' + name

        if not getattr(self, internal_name, None):
            self.logger.error(f'Attribute {name} not found in {self.__class__.__name__}', extra=self.log_args)
            raise SystemExit

        setattr(self, internal_name, new_value)

    def get_packable_attributes(self, full):
        attrs = []
        for attr_name in self.packable:
            attrs.append(getattr(self, '_' + attr_name))
        if full:
            for attr_name in self.packable_full:
                attrs.append(getattr(self, '_' + attr_name))
        return attrs

    def get_packable_attributes_with_names(self, full):
        attrs = self.get_packable_attributes(full)        
        attrs_names = self.packable + self.packable_full if full else self.packable
        return zip(attrs_names, attrs)

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

class CommunicationFrame(CommunicationStructure):

    def __init__(self, byteorder='>'):
        CommunicationStructure.__init__(self, byteorder)

    def change_data_type(self, msg_type):
        pass

    def get_data(self):
        pass

    def set_data(self, *args, **kwargs):
        pass
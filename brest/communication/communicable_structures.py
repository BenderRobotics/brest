#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.communicable_structures
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base functionality for message
    creating using packable types.

    :copyright: 2021 Bender Robotics
"""

import logging

class Endianness():
    BIG = '>'
    LITTLE = '<'

class Packable():
    """
    Base class for structures, that can be serialized into and deserialized from a bytearray.
    """

    def __init__(self):
        self.byteorder = Endianness.LITTLE

    def pack(self, data, offset):
        """
        Serializes packable attributes to bytearray.

        If this method is called without parameters, this method will behave as
        top level and all serialized data will be saved into `raw_data` attribute
        on current object.

        :param data: Previous bytes
        :type  data: bytearray
        :param offset: Number of already packed bites
        :type  data: int
        """

        raise NotImplementedError('This structure can\'t be packed')

    def unpack(self, data, offset):
        """
        De-serializes from bytearray to packable attributes

        If this method is called without parameters, this method will behave as
        top level and all serialized data in `raw_data` attribute will be
        de-serialized and values saved in correspoding attributes.

        :param data: raw_data bytes
        :type  data: bytearray
        :param offset: Number of already unpacked bites
        :type  data: int
        """

        raise NotImplementedError('This structure can\'t be unpacked')

    def is_padded(self, data, offset):
        """
        Checks if offset is aligned to bytes.

        :param data: Currently packed data
        :type  data: bytearray
        :param offset: Number of currently packed/unpacked bites
        :type  data: int
        :returns: True if offset is aligned to bytes, False othervise
        :rtype: bool
        """

        return offset // 8 == len(data) and (offset % 8 == 0 or offset % 8 == 8)

    def pad_size(self, offset):
        """
        Returns number of bites needed for offset to be byte aligned.

        :param offset: Number of currently packed/unpacked bites.
        :type  offset: int
        :returns: Returns number of bites needed for offset to be byte aligned
        :rtype: int
        """

        pad = 8 - (offset % 8)
        return pad if pad != 8 else 0

class CommunicationStructure(Packable):
    """
    Base class for message creation.

    This class can be also used as data type in case, where you don't need to
    unpack any data.

    Derived from: :class:`~brest.communication.Packable`

    :param byteorder: Order of bytes `'>' - Big endian`; `'<' - Little endian`
    :type  byteorder: str
    """

    def __init__(self, byteorder = Endianness.LITTLE):
        Packable.__init__(self)
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        #: Raw data.
        #: Pack() method saves serialized bytes into this.
        #: Unpack() method read bytes for de-serialization from this.
        self.raw_data = bytearray()
        #: Order of bytes
        self.byteorder = byteorder
        #: List of attributes, that will be packed
        self.packable = []
        #: List of attributes, that will be packed only if `full=True` is specified
        self.packable_full = []
        #: Indicates if full pack should be done
        self.full = True

        self.value_ = self

    def __eq__(self, other):
        for pair in zip(self.get_packable_attributes(True), other.get_packable_attributes(True)):
            if pair[0].value_ != pair[1].value_:
                return False
        return True

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['logger']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.logger = self.logger = logging.getLogger('brest')

    def add(self, name, value, byteorder = None, full_only = False, len_attr = None):
        """
        Adds packable type as an attribute.

        Name can\'t be `value_` or `lengths_` which are reserved for internal values.
        If len_attr is specified, that attribute is treated as a byte length for this attribute.

        :param name: Name of a attribute
        :type  name: str
        :param value: Value to be saved into the parameter
        :type  value: :class:`~brest.communication.Packabl e`
        :param full_only: Specifies if this parameter should be packet only if
                          full packing is requested.
        :type  full_only: bool
        :param len_attr: Attribute is treated as a length for this attribute.
        :type len_attr: str
        """

        if name in ['value_']:
            self.logger.error('Name can\'t be `{}` which is reserved for internal values'.format(name), extra=self.log_args)
            raise SystemExit(1)

        if not issubclass(value.__class__, Packable):
            self.logger.error('Value in `{}` must derive from Packable class'.format(name), extra=self.log_args)
            raise SystemExit(1)

        internal_name = '_' + name
        value.byteorder = self.byteorder           # set message specific byteorder
        if byteorder:
            value.byteorder = byteorder
        setattr(self, internal_name, value)        # create attribute
        setattr(self.__class__, name, property(
            lambda self: getattr(self, internal_name).value_,                           # create getter
            lambda self, value: setattr(getattr(self, internal_name), 'value_', value)) # create setter
        )
        self.packable_full.append(name) if full_only else self.packable.append(name)

        if len_attr:
            attr = getattr(self, '_' + len_attr, None)
            if not attr:
                self.logger.error('Attribute `{}` is not defined'.format(len_attr), extra=self.log_args)
                raise SystemExit
            value.len_attr = attr

    def change(self, name, new_value):
        """
        Changes data type of an attribute.

        This method does not preserve previous value of an attribute.

        :param name: Name of an attribute
        :type  name: str
        :param new_value: New type
        :type  new_value: :class:`~brest.communication.Packable`
        """

        internal_name = '_' + name

        if not getattr(self, internal_name, None):
            self.logger.error('Attribute {} not found in {}'.format(name, self.__class__.__name__), extra=self.log_args)
            raise SystemExit(1)

        setattr(self, internal_name, new_value)

    def get_packable_attributes(self, full):
        """
        Returns packable attributes.

        :param full: Indicates if full only attributes should be return as well
        :type  full: bool
        :returns: Packable attributes
        :rtype: list of :class:`~brest.communication.Packable`
        """

        attrs = []
        for attr_name in self.packable:
            attrs.append(getattr(self, '_' + attr_name))
        if full:
            for attr_name in self.packable_full:
                attrs.append(getattr(self, '_' + attr_name))
        return attrs

    def get_packable_attributes_with_names(self, full):
        """
        Returns packable attributes with theirs defined names.

        :param full: Indicates if full only attributes should be return as well
        :type  full: bool
        :returns: Packable attributes
        :rtype: list of :class:`~brest.communication.Packable`
        """

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
    """
    Base abstract class for representing a frame.

    Derived from: :class:`~brest.communication.CommunicationStructure`

    :param byteorder: Order of bytes `'>' - Big endian`; `'<' - Little endian`
    :type  byteorder: str
    """

    def __init__(self, byteorder='>'):
        CommunicationStructure.__init__(self, byteorder)

    def change_data_type(self, msg_type):
        """
        Changes type of data payload.

        Only class type should be passed. Use
        :meth:`~brest.communication.CommunicationStructure.change`
        method to change data type of an data attribute.
        """

        pass

    def get_data(self):
        """
        Returns data payload.
        """

        pass

    def set_data(self, *args, **kwargs):
        """
        Sets the data payload.

        Also if header needs to be changed after new data insertion,
        do it here. This method has no firm parameters definition, so
        feel free to define them as ne need.
        """

        pass

    def is_frame_valid(self, rec_frame, sent_frame):
        """
        Validates if the received frame is valid.

        :param rec_frame: Received frame
        :type  rec_frame: :class:`brest.communication.CommunicationFrame`
        :param sent_frame: Sent frame in case of transcieve communication,
                           othervise `None`
        :type  sent_frame: :class:`brest.communication.CommunicationFrame`
        :returns: Validity of a received frame
        :rtype: bool
        """

        return True

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.communication.types
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements packable types that are
    used to define a message.

    :copyright: 2020 Bender Robotics
"""

import struct

from math import ceil, log2

from brest.communication import Packable

class uint8_t(Packable):
    """
    Unsigned 8-bit integer.
    """

    def __init__(self, value = None):
        Packable.__init__(self)
        self.size = 8
        self.value_ = value if value else 0

    def pack(self, data, offset):
        data += struct.pack('B', (self.value_ & 0xFF))
        return offset + self.size + self.pad_size(offset)

    def unpack(self, data, offset):
        offset += self.pad_size(offset)
        b_offset = offset // 8
        self.value_ = struct.unpack_from('B', data, b_offset)[0]
        return offset + self.size

class uint16_t(Packable):
    """
    Unsigned 16-bit integer.
    """

    def __init__(self, value = None):
        Packable.__init__(self)
        self.size = 16
        self.value_ = value if value else 0

    def pack(self, data, offset):
        data += struct.pack(self.byteorder + 'H', self.value_)
        return offset + self.size + self.pad_size(offset)

    def unpack(self, data, offset):
        offset += self.pad_size(offset)
        b_offset = offset // 8
        self.value_ = struct.unpack_from(self.byteorder + 'H', data, b_offset)[0]
        return offset + self.size

class sint16_t(Packable):
    """
    Signed 16-bit integer.
    """

    def __init__(self, value = None):
        Packable.__init__(self)
        self.size = 16
        self.value_ = value if value else 0

    def pack(self, data, offset):
        data += struct.pack(self.byteorder + 'h', self.value_)
        return offset + self.size + self.pad_size(offset)

    def unpack(self, data, offset):
        offset += self.pad_size(offset)
        b_offset = offset // 8
        self.value_ = struct.unpack_from(self.byteorder + 'h', data, b_offset)[0]
        return offset + self.size

class uint32_t(Packable):
    """
    Unsigned 32-bit integer.
    """

    def __init__(self, value = None):
        Packable.__init__(self)
        self.size = 32
        self.value_ = value if value else 0

    def pack(self, data, offset):
        data += struct.pack(self.byteorder + 'I', self.value_)
        return offset + self.size + self.pad_size(offset)

    def unpack(self, data, offset):
        offset += self.pad_size(offset)
        b_offset = offset // 8
        self.value_ = struct.unpack_from(self.byteorder + 'I', data, b_offset)[0]
        return offset + self.size

class str_t(Packable):
    """
    String with variable lenght. Can\'t be unpacked!.
    """

    def __init__(self, value):
        Packable.__init__(self)
        self._value = str(value)

    @property
    def size(self):
        return len(self.value_) * 8

    @property
    def value_(self):
        return self._value

    @value_.setter
    def value_(self, value):
        self._value = str(value)

    def pack(self, data, offset):
        data += struct.pack(self.byteorder + str(len(self.value_)) + 's', self.value_.encode('utf-8'))
        return offset + self.size

class bool_t(Packable):
    """
    Boolean packed as a whole byte
    """

    def __init__(self, value = None):
        Packable.__init__(self)
        self.size = 8
        self.value_ = value if value else False

    def pack(self, data, offset):
        data += struct.pack('B', 0x01 if self.value_ else 0x00)
        return offset + self.size + self.pad_size(offset)

    def unpack(self, data, offset):
        offset += self.pad_size(offset)
        b_offset = offset // 8
        self.value_ = True if struct.unpack_from('B', data, b_offset)[0] else False
        return offset + self.size

class bit_t(Packable):
    """
    Boolean packed on `bit` position in a byte.
    """

    def __init__(self, value = None, bit = 0):
        Packable.__init__(self)
        self.size = 1
        self.value_ = value if value else False
        self.bit = bit

    def pack(self, data, offset):
        b = struct.pack('B', (1 << self.bit) if self.value_ else 0)
        if not self.is_padded(data, offset):
            data[-1] |= int().from_bytes(b, 'big')
        else:
            data += b

        return offset + self.size

    def unpack(self, data, offset):
        b_offset = offset // 8
        data = data[b_offset]
        self.value_ = True if (data >> self.bit) & 0x01 > 0 else False
        return offset + self.size

class nlist_t(Packable):
    """
    Fixed length list of any packable type except bit_t.
    """

    def __init__(self, value, num_items, type_t):
        self.type_t = type_t()
        Packable.__init__(self)
        self.num_items = num_items
        self.size = self.type_t.size * self.num_items
        self.value_ = value

    @property
    def byteorder(self):
        return self.type_t.byteorder

    @byteorder.setter
    def byteorder(self, value):
        self.type_t.byteorder = value

    def pack(self, data, offset):
        # value not None
        for i in range(self.num_items):
            self.type_t.value = self.value_[i]
            offset = self.type_t.pack(data, offset)
        return offset

    def unpack(self, data, offset):
        self.value_ = []
        offset += self.pad_size(offset)
        for i in range(self.num_items):
            offset = self.type_t.unpack(data, offset)
            self.value_.append(self.type_t.value_)
        return offset

class vlist_t(Packable):
    """
    Variable length list of any packable type except bit_t.
    """

    def __init__(self, value, type_t):
        self.type_t = type_t()
        Packable.__init__(self)
        self._value_ = value
        self.len_attr = None

    @property
    def value_(self):
        return self._value_

    @value_.setter
    def value_(self, value):
        self._value_ = value
        self.len_attr.value_ = int(self.type_t.size / 8 * len(self._value_))

    @property
    def byteorder(self):
        return self.type_t.byteorder

    @byteorder.setter
    def byteorder(self, value):
        self.type_t.byteorder = value

    def pack(self, data, offset):
        for i in range(len(self.value_)):
            self.type_t.value_ = self.value_[i]
            offset += self.type_t.pack(data, offset)
        return offset

    def unpack(self, data, offset):
        values = []
        for i in range(int(self.len_attr.value_ / (self.type_t.size / 8))):
            offset = self.type_t.unpack(data, offset)
            values.append(self.type_t.value_)
        self.value_ = values
        return offset

class bit_nlist_t(Packable):
    """
    Fixel length list of bit_t.
    """

    def __init__(self, value, num_items):
        Packable.__init__(self)
        self.num_items = num_items
        self.size = self.num_items // 8 + 1 if self.num_items // 8 > 0 else self.num_items // 8
        self.value_ = value

    def pack(self, data, offset):
        bit = 0
        for i in range(self.num_items):
            b = struct.pack('B', (1 << bit) if self.value_[i] else 0)
            if not self.is_padded(data, offset):
                data[-1] |= int().from_bytes(b, 'big')
            else:
                data += b
            offset += 1

            bit += 1
            if bit > 7:
                bit = 0
        return offset

    def unpack(self, data, offset):
        bit = 0
        self.value_ = []
        for i in range(self.num_items):
            b_offset = offset // 8
            v = data[b_offset]
            self.value_.append(True if (v >> bit) & 0x01 > 0 else False)
            offset += 1

            bit += 1
            if bit > 7:
                bit = 0
        return offset

class bit_uint_t(Packable):
    """
    Unsigned int packet on less than byte
    """

    def __init__(self, size, value=None, bit_offset=None):
        Packable.__init__(self)
        self.size = size
        self.value_ = value if value else 0
        self.bit_offset = bit_offset if bit_offset else 0

    def pack(self, data, offset):
        num = (self.value_ & (2 ** self.size - 1)) << self.bit_offset
        if self.is_padded(data, offset):
            data += struct.pack('B', num)
        else:
            data[-1] |= num
        return offset + self.size

    def unpack(self, data, offset):
        b_offset = offset // 8
        num = struct.unpack_from('B', data, b_offset)[0]
        self.value_ = (num & ((2 ** self.size - 1) << self.bit_offset)) >> self.bit_offset
        return offset + self.size

class enum_t(Packable):
    """
    Enumeration created using :class:`~enum.Enum`

    :param enum: Enumeration to referece
    :type  enum: :class:`~enum.Enum`
    :param value: Value from enumeration to pack
    :type  value: :class:`~enum.Enum`
    :param size: Size to be packet in bits. If omitted, enum
                 will be packet onto minimal number of bits
    :type  size: int
    """

    def __init__(self, enum, value=None, size=None):
        Packable.__init__(self)
        self.enum = enum
        self.value_ = value
        self.size = calc_size = ceil(log2(len(list(enum))))
        if size and size > calc_size:
                self.size = size

    def pack(self, data, offset):
        as_int = self.value_.value if self.value_ else 0
        as_list = [bool(as_int >> i & 0x01) for i in range(0, self.size)]
        as_list.reverse()
        bit_list = bit_nlist_t(as_list, self.size)
        offset = bit_list.pack(data, offset)
        return offset

    def unpack(self, data, offset):
        value = 0
        bit_list = bit_nlist_t([], self.size)
        offset = bit_list.unpack(data, offset)
        bit_list.value_.reverse()
        for i in range(0, self.size):
            if bit_list.value_[i]:
                value |= 2 ** i
        self.value_ = self.enum(value)
        return offset

class checksum_t(Packable):
    """
    Calculates the checksum from previous bytes using
    given function.

    The function must have at least one parameter where
    bytearray will be passed and return `type_t` compatible
    argument.

    :param type_t: Type in the checksum will be saved.
    :type  type_t: :class:`brest.communication.Packable`
    :param checksum_func: Function which calculates the checksum
    :type  checksum_func: Callable
    """

    def __init__(self, type_t, checksum_func):
        self.type_t = type_t()
        Packable.__init__(self)
        self.size = self.type_t.size
        self.checksum_func = checksum_func

    @property
    def value_(self):
        return self.type_t.value_

    @property
    def byteorder(self):
        return self.type_t.byteorder

    @byteorder.setter
    def byteorder(self, value):
        self.type_t.byteorder = value

    def pack(self, data, offset):
        self.type_t.value_ = self.checksum_func(data)
        offset = self.type_t.pack(data, offset)
        return offset

    def unpack(self, data, offset):
        offset = self.type_t.unpack(data, offset)
        return offset

class fill_t(Packable):
    """
    Fills N bytes with a uint8 value
    """

    def __init__(self, value=None, num_bytes=1):
        Packable.__init__(self)
        self.size = 8 * num_bytes
        self.value_ = value if value else 0
        self.num_bytes = num_bytes

    def pack(self, data, offset):
        for _ in range(0, self.num_bytes):
            data += struct.pack('B', self.value_)
        return offset + self.size + self.pad_size(offset)

    def unpack(self, data, offset):
        return offset + self.size + self.pad_size(offset)

class pad_t(Packable):
    """
    Pads the offset to the first full byte.
    """

    def __init__(self):
        Packable.__init__(self)
        self.value_ = 0
        self.size = 0

    def pack(self, data, offset):
        return offset + self.pad_size(offset)

    def unpack(self, data, offset):
        return offset + self.pad_size(offset)

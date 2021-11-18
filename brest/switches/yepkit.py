# -*- coding: utf-8 -*-
"""
    brest.switches.hid_switch.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract for switches.

    :copyright: 2021 Bender Robotics
"""

from brest.switches.switches import Switches
from brest.communication import HIDCommunicable
from brest.communication import CommunicationStructure
from brest.communication.types import uint8_t, bit_uint_t, nlist_t, vlist_t


class BaseFrame(CommunicationStructure):
    def __init__(self):
        CommunicationStructure.__init__(self)
        self.add('status', uint8_t(0))

class ResponseFrame(BaseFrame):
    def __init__(self):
        BaseFrame.__init__(self)
        self.add('data', nlist_t(None, 30, uint8_t))

class ChannelCommand(BaseFrame):
    def __init__(self, command):
        BaseFrame.__init__(self)
        self.add('command', bit_uint_t(4, command >> 4, 4))
        self.add('channel', bit_uint_t(4, 0, 0))

class ChannelResponse(BaseFrame):
    def __init__(self):
        BaseFrame.__init__(self)
        self.add('value', bit_uint_t(4, 0, 4))
        self.add('channel', bit_uint_t(4, 0, 0))

class ReadIOCommand(BaseFrame):
    def __init__(self, command):
        BaseFrame.__init__(self)
        self.add('command', uint8_t(command))
        self.add('port', uint8_t())

class WriteCommand(BaseFrame):
    def __init__(self, command):
        BaseFrame.__init__(self)
        self.add('command', uint8_t(command))
        self.add('port', uint8_t())
        self.add('value', uint8_t())

class Command(BaseFrame):
    def __init__(self, command):
        BaseFrame.__init__(self)
        self.add('command', uint8_t(command))

class ControlCommand(BaseFrame):
    def __init__(self, command):
        BaseFrame.__init__(self)
        self.add('command', uint8_t(command))
        self.add('value', uint8_t())

class InfoCommand(BaseFrame):
    def __init__(self, command, subcommand):
        BaseFrame.__init__(self)
        self.add('command', uint8_t(command))
        self.add('subcommand', uint8_t(subcommand))

class I2CControlCommand(InfoCommand):
    def __init__(self, command, subcommand):
        InfoCommand.__init__(self, command, subcommand)
        self.add('value', uint8_t())

class I2CReadCommand(InfoCommand):
    def __init__(self, command, subcommand):
        InfoCommand.__init__(self, command, subcommand)
        self.add('address', uint8_t())
        self.add('size', uint8_t())

class I2CWriteCommand(InfoCommand):
    def __init__(self, command, subcommand):
        InfoCommand.__init__(self, command, subcommand)
        self.add('address', uint8_t())
        self.add('size', uint8_t())
        self.add('data', nlist_t([], 1, uint8_t))


class YepkitSwitch(Switches, HIDCommunicable):
    """
    YKUSH Yepkit switchable USB hub.

    Derived from :class:`~brest.switches.Switches`, :class:`~brest.communication.HIDCommunicable`

    This class implements API for YKUSH Yepkit switchable hub - enables turning USB devices ON/OFF on HW level.

    :param params: Construction parameters
    :type params: dict

    Implicit interface definition::

        interface:
            type: 'hid'
            vid:  0x04d8
            pid:  0xf11b
    """

    Switches.KNOWN['YepkitSwitch'] = {
        'type': 'hid',
        'vid': 0x04d8,
        'pid': 0xf11b,
    }

    class Commands:
        """
        Available commands.
        """
        STATE_ON = ChannelCommand(0x10)
        STATE_OFF = ChannelCommand(0x00)
        GET_STATE = ChannelCommand(0x20)
        GET_ALL_STATE = Command(0x2a)
        WRITE_IO = WriteCommand(0x31)
        READ_IO = ReadIOCommand(0x30)
        CONFIG_PORT = WriteCommand(0x41)
        RESET = Command(0x55)
        GPIO_CTRL = ControlCommand(0x32)
        ENTER_BOOTLOADER = Command(0x42)
        I2C_CONTROL = I2CControlCommand(0x51, 0x01)
        I2C_GATEWAY_CONTROL = I2CControlCommand(0x51, 0x02)
        I2C_SET_ADDRESS = I2CControlCommand(0x51, 0x03)
        I2C_WRITE = I2CWriteCommand(0x52, 0x01)
        I2C_READ = I2CReadCommand(0x52, 0x02)
        GET_VERSION_BL = InfoCommand(0x61, 0x01)
        GET_VERSION_FW = InfoCommand(0x61, 0x02)

    COMMAND_SUCCES = 0x1
    PACKET_SIZE = 64

    def __init__(self, params):
        Switches.__init__(self, params)
        HIDCommunicable.__init__(self, params['interface'])
        self.STATES = 2
        self.CHANNELS = 3
        self.IO_PORTS = 3

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if (key >= self.CHANNELS or key < 0):
                raise KeyError('Index out of range')
        elif isinstance(key, str):
            key = self._aliases[key]
        else:
            raise TypeError('Invalid value type')

        self._write_state(key, value)

    def __getitem__(self, key):
        if isinstance(key, int):
            if (key >= self.CHANNELS or key < 0):
                raise KeyError('Index out of range')
        elif isinstance(key, str):
            key = self._aliases[key]
        else:
            raise TypeError('Invalid value type')

        return self._read_states()[key]

    def _send_receive(self, cmd_raw):
        cmd = cmd_raw
        self.write_raw(cmd)
        raw = self.read_raw(size=self.PACKET_SIZE)

        response = ResponseFrame()
        response.unpack(bytes(raw))

        return response

    def _read_states(self):
        command = self.Commands.GET_ALL_STATE
        command.pack()

        response = self._send_receive(command.raw_data)

        if response.status == self.COMMAND_SUCCES:
            ports =  response.data[:self.CHANNELS + 1]
            return tuple(p > 0x10 for p in ports)

        return None

    def _write_state(self, channel, state):
        if state:
            command = self.Commands.STATE_ON
        else:
            command = self.Commands.STATE_OFF

        command.channel = channel + 1
        command.pack()
        self._send_receive(command.raw_data)

    def detect_model(self):
        pass

    def write_io(self, port, value):
        if port > self.IO_PORTS or port < 0:
            raise ValueError("Invalid port number")

        command = self.Commands.WRITE_IO
        command.port = port + 1
        command.value = value

        command.pack()

        self._send_receive(command.raw_data)

    def read_io(self, port):
        if port > self.IO_PORTS or port < 0:
            raise ValueError("Invalid port number")

        command = self.Commands.READ_IO
        command.port = port + 1
        command.pack()

        response = self._send_receive(command.raw_data)

        return response.data[2]

    def config_port(self, port, value):
        command = self.Commands.CONFIG_PORT
        command.change('port', uint8_t(port))
        command.change('value', uint8_t(value))
        command.pack()

        self.write_raw(command.raw_data)

    def reset(self):
        command = self.Commands.RESET
        command.pack()

        self._send_receive(command.raw_data)

    def gpio_control(self, state):
        command = self.Commands.GPIO_CTRL
        if state:
            command.change('value', uint8_t(0x01))
        else:
            command.change('value', uint8_t(0x00))

        command.pack()

        self.write_raw(command.raw_data)

    def enter_bootloader(self):
        command = self.Commands.ENTER_BOOTLOADER
        command.pack()

        self.write_raw(command.raw_data)

    def i2c_control(self, state):
        command = self.Commands.I2C_CONTROL

        if state:
            command.change('value', uint8_t(0x01))
        else:
            command.change('value', uint8_t(0x00))

        command.pack()

        self.write_raw(command.raw_data)

    def i2c_gateway_control(self, state):
        command = self.Commands.I2C_GATEWAY_CONTROL

        if state:
            command.change('value', uint8_t(0x01))
        else:
            command.change('value', uint8_t(0x00))

        command.pack()

        self.write_raw(command.raw_data)

    def i2c_set_address(self, address):
        command = self.Commands.I2C_SET_ADDRESS
        command.change('value', address)
        command.pack()

        self.write_raw(command.raw_data)

    def i2c_write(self, address, data):
        # TODO check data len < 60, and iterable
        data_len = len(data)

        command = self.Commands.I2C_WRITE
        command.change('address', uint8_t(address))
        command.change('size', uint8_t(data_len))
        command.change('data', nlist_t(data, data_len, uint8_t))
        command.pack()

        self.write_raw(command.raw_data)

    def i2c_read(self, address, size):
        command = self.Commands.I2C_READ
        command.change('address', uint8_t(address))
        command.change('size', uint8_t(size))
        command.pack()

        self.write_raw(command.raw_data)
        return self.read_raw(size=size)

    def get_bl_version(self):
        """
        Get bootloader version.

        :return: Version of BL in format X.Y.Z
        :rtype: str
        """
        command = self.Commands.GET_VERSION_BL
        command.pack()

        self.write_raw(command.raw_data)
        fw = self.read_raw(size=5)

        if (fw[0] != 0x01) and (fw[0] != 0x61):
            return "0.10.0"

        return f"{fw[2]}.{fw[3]}.{fw[4]}"

    def get_fw_version(self):
        """
        Get FW version.

        :return: Version of FW in format X.Y.Z
        :rtype: str
        """
        command = self.Commands.GET_VERSION_FW
        command.pack()

        self.write_raw(command.raw_data)
        fw = self.read_raw(size=5)

        if (fw[0] != 0x01) and (fw[0] != 0x61):
            return "1.0.0"

        return f"{fw[2]}.{fw[3]}.{fw[4]}"

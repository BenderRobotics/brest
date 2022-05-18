#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.flashers.STLink
    ~~~~~~~~~~~~~~~~~~~~

    This module implements ST-LinkV2/V3 programmers.

    :copyright: 2022 Bender Robotics
"""

import os
import re
import sys
import tempfile

from shutil import which
from brest.flashers import Flashers
from brest.communication import FlasherCommunicable
from brest.log_subprocess import run, PIPE, STDOUT


class STLink(Flashers, FlasherCommunicable):
    """
    STMicroelectronics programmer

    Derived from :class:`~brest.flashers.Flashers`, :class:`~brest.communication.FlasherCommunicable`

    :param params: Construction parameters
    :type  params: dict

    Supported models: V2, V3(experimental)

    Supported CLI: STM32_Programmer_CLI (Cube version)

    Implicit interface definition::

        interface:
            type:       'flashers'
            list_type:  'cli',
            list_cmd:   ['--list']
            list_regex: r'st-link\s*probe\s*\d+\s*:\s*.*\s*st-link sn\s*:\s*(\w+)\s*.*\s*st-link fw\s*:\s*(\w+)'
            utility:    Windows - C:/ProgramFiles(x86)/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe
                        Linux   - STM32_Programmer_CLI
    """

    Flashers.KNOWN['STLink'] = {
        'type': 'flashers',
        'list_type': 'cli',
        'list_cmd': ['--list'],
        'list_regex': r'st-link\s*probe\s*\d+\s*:\s*.*\s*st-link sn\s*:\s*(\w+)\s*.*\s*st-link fw\s*:\s*(\w+)',
        'utility': str('{0};{1};{2}'.format(os.path.join(
            'STM32_Programmer_CLI.exe',
        ), os.path.join(
            'C:/', 'Program Files (x86)', 'STMicroelectronics', 'STM32Cube', 'STM32CubeProgrammer', 'bin', 'STM32_Programmer_CLI.exe'
        ), os.path.join(
            'C:/', 'Program Files', 'STMicroelectronics', 'STM32Cube', 'STM32CubeProgrammer', 'bin', 'STM32_Programmer_CLI.exe'
        ))) if sys.platform == 'win32' else os.path.join('STM32_Programmer_CLI')
    }

    def __init__(self, params):
        Flashers.__init__(self, params)
        self._verbosity = '1'
        self._timeout = 2
        FlasherCommunicable.__init__(self, params['interface'])

        if which(self._utility) is None:
            self.logger.error("Utility %s is not executable" % self._utility)
            raise ValueError

        self.mark_taken(self)

    def __del__(self):
        FlasherCommunicable.release(self)

    def flash(self, file="", address="", flashloader="", timeout=None):
        if timeout is None:
            timeout = self._timeout

        if address == "":
            address = self._address

        if file == "":
            if self._file == "":
                self.logger.error("No file to flash", extra=self.log_args)
                return None
            file = self._file

        if flashloader == "":
            flashloader = self._flashloader

        address = self._unify_address(address)

        # prepare command
        command = []
        if flashloader != "":
            command += ['-el', flashloader]
        command += ['-d', file]
        if address != '':
            command.append(address)
        command += ['-v']

        self.connect()
        process = run(self.__parse_connect() + command, stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to flash MCU memory{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()

        return process

    def write(self, address, data, timeout=None):
        if timeout is None:
            timeout = self._timeout

        command = []
        address = self._unify_address(address)

        tmp_file = tempfile.NamedTemporaryFile(mode='wb', suffix=".bin", delete=False)
        tmp_file.write(bytes(data))
        tmp_file.flush()

        # file need to be closed so CLI can open it
        tmp_file.close()

        command += ['-w', tmp_file.name, address, '--skipErase']

        self.connect()
        process = run(self.__parse_connect() + command, stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)

        os.remove(tmp_file.name)

        if process.returncode != 0:
            self.logger.error('Unable to write to MCU memory{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()
        return process

    def mass_erase(self, timeout=None):
        if timeout is None:
            timeout = self._timeout

        self.connect()
        process = run(self.__parse_connect() + ['-e', 'all'], stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to perform mass erase{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()
        return process

    def erase_sector(self, sector, timeout=None):
        if timeout is None:
            timeout = self._timeout

        if isinstance(sector, tuple) or isinstance(sector, list):
            if len(sector) < 1:
                raise ValueError('Iterable need to have atleast one member')

            if not isinstance(sector[0], int):
                raise ValueError('Iterable[0] is not integer')

            if len(sector) < 2:
                sector = str(sector[0])
            else:
                if not isinstance(sector[1], int):
                    raise ValueError('Iterable[1] is not integer')
                sector = '[%s %s]' % (str(sector[0]), str(sector[1]))
        elif isinstance(sector, int):
            if sector < 0:
                raise ValueError('Only positive sectors')
            sector = str(sector)
        else:
            raise ValueError('Only iterable or integer is supported')

        self.connect()
        process = run(self.__parse_connect() + ['-e', sector], stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to erase sector{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()
        return process

    def read(self, address, size, timeout=None):
        if timeout is None:
            timeout = self._timeout

        address = self._unify_address(address)
        self.connect()
        process = run(self.__parse_connect() + ['-r8', address, hex(size)], stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to perform read from MCU memory{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()

        data = process.stdout.read().decode()
        data_regex = r"0x\w+\s*:\s*((\w+ *)*\w+)"

        matches = re.finditer(data_regex, data, re.MULTILINE | re.IGNORECASE)

        out = []
        for match in matches:
            data = match.group(1).strip("\n").split(" ")

            out.extend(int(i, 16) for i in data if data != '')

        return out

    def read_to_file(self, address, size, file, timeout=None):
        if timeout is None:
            timeout = self._timeout

        address = self._unify_address(address)

        _, file_extension = os.path.splitext(file)
        if file_extension not in ['.bin', '.hex', '.srec']:
            self.logger.error(
                'Invalid file extension. Only bin, hex and srec are supported.', extra=self.log_args)
            return

        if not os.path.isfile(file):
            try:
                with open(file, 'w') as _:
                    pass
            except Exception:
                self.logger.error('Unable to create %s' % file, extra=self.log_args)
                return

        self.connect()
        process = run(self.__parse_connect() + ['-r', address, str(hex(size)), file], stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to read to file{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()
        return process

    def soft_reset(self, timeout=None):
        if timeout is None:
            timeout = self._timeout

        self.connect()
        process = run(self.__parse_connect() + ['-rst'], stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to perform soft reset{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()
        return process

    def hard_reset(self, timeout=None):
        if timeout is None:
            timeout = self._timeout

        self.connect()
        process = run(self.__parse_connect() + ['-hardRst'], stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to perform hard reset{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()
        return process

    def __parse_connect(self, *args):
        connect_args = [self._utility]
        for arg in args:
            if arg != '':
                connect_args.append(arg)

        connect_args += ['-vb', self._verbosity]

        if self._quiet:
            connect_args.append('-q')

        connect_args.append('-c')
        connect_args.append('port=' + self._port)

        if self._frequency != '':
            connect_args.append('freq=' + self._frequency)

        if self._serial_number != '':
            connect_args.append('sn=' + self._serial_number)

        if self._mode != '':
            connect_args.append('mode=' + self._mode)

        if self._reset != '':
            connect_args.append('reset=' + self._reset)

        return connect_args

    def connect(self, timeout=None):
        if timeout is None:
            timeout = self._timeout

        process = run(self.__parse_connect(), stdout=PIPE,
                      stderr=STDOUT, timeout=timeout)
        if process.returncode != 0:
            self.logger.error('Unable to connect{0}{1}'.format(os.linesep, process.stdout.read().decode()), extra=self.log_args)
            raise ConnectionError()

        decode = process.stdout.read().decode()
        device_regex = r'device\s*name\s*:\s*([\d\w]*)'
        match = re.search(device_regex, decode, re.MULTILINE | re.IGNORECASE)
        if match:
            name = match.group(1).replace('x', '').lower()
            if name in self._device.lower() or "" == self._device:
                return

        self.logger.error('Unexpected device detected (Excpected: {0}, Detected: {1})'.format(self._device, name), extra=self.log_args)
        raise ConnectionError

    def default_mode(self, value):
        value = str(value)
        if value.lower() not in ['under_reset', 'hotplug', 'normal']:
            self.logger.error("Invalid value of mode", extra=self.log_args)
            return False

        self._mode = value.upper()
        return True

    def default_reset(self, value):
        value = str(value)
        if value == 'sw':
            self._reset = 'SWrst'
        elif value == 'hw':
            self._reset = 'HWrst'
        elif value == 'core':
            self._reset = 'Crst'
        else:
            self.logger.error("Invalid value for reset", extra=self.log_args)
            return False

        return True

    def default_verbosity(self, value):
        try:
            value = int(value)
        except TypeError:
            self.logger.error("Invalid value for verbosity", extra=self.log_args)
            return False

        if value < 1 or value > 3:
            self.logger.error("Invalid value for verbosity", extra=self.log_args)
            return False

        self._verbosity = str(value)

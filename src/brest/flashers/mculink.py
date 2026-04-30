#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.flashers.MCULink
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements NXP MCU-Link programmers.

    :copyright: 2024 Bender Robotics
"""

import os
import re
import sys
import tempfile
import logging

from shutil import which
from brest.flashers import Flashers
from brest.communication import FlasherCommunicable
from brest.log_subprocess import run, PIPE, STDOUT


CLI_UTIL_USAGE_PATH = 'crt_emu_cm_redlink.exe'
CLI_UTIL_PROBING_PATH = 'rltool.exe'
CLI_UTIL_SERVER_PATH = 'redlinkserv.exe'
SCRIPT_PATH = 'Scripts'

pattern = re.compile(r'^MCUXpressoIDE\S*')
dir_path = os.path.join('C:/', 'NXP')
try:
    contents = os.listdir(dir_path)
    for item in contents:
        match = pattern.match(item)
        if match:
            dir_name = match.group(0)
            break
    CLI_UTIL_USAGE_PATH = os.path.join(dir_path, dir_name, 'ide', 'binaries', 'crt_emu_cm_redlink.exe')
    CLI_UTIL_PROBING_PATH = os.path.join(dir_path, dir_name, 'ide', 'binaries', 'rltool.exe')
    CLI_UTIL_SERVER_PATH = os.path.join(dir_path, dir_name, 'ide', 'binaries', 'redlinkserv.exe')
    SCRIPT_PATH = os.path.join(dir_path, dir_name, 'ide', 'binaries', 'Scripts', '{}')
except Exception as ex:
    logger = logging.getLogger('brest-MCULink')
    logger.warning(
        msg=f'Could not find an instance of MCUXpresso. Looked in {dir_path}.',
        exc_info=True
    )


class MCULink(Flashers, FlasherCommunicable):
    """
    NXP MCULink programmer

    Derived from :class:`~brest.flashers.Flashers`, :class:`~brest.communication.FlasherCommunicable`

    :param params: Construction parameters
    :type  params: dict

    Used CLIs: MCUXpresso: rltool, crt_emu_cm_redlink, redlinkserv

    Developed with MCUXpressoIDE_11.6.1_8255

    Currently supports only methods: flash, mass_erase, read, write

    Implicit interface definition::

        interface:
            type:       'flashers'
            list_type:  'cli',
            list_cmd:   ['-c', 'PROBELIST']
            list_regex: 'Index = \\s*\\d+\\s*Manufacturer = .*\\s*Description = .*\\s*Serial Number = (\\S+)'
            utility:    Windows
                            - probing - 'C:/NXP/MCUXpressoIDE_11.6.1_8255/ide/binaries/rltool.exe'
                            - flashing / writing - 'C:/NXP/MCUXpressoIDE_11.6.1_8255/ide/binaries/crt_emu_cm_redlink.exe'
                            - reading - 'C:/NXP/MCUXpressoIDE_11.6.1_8255/ide/binaries/redlinkserv.exe'
                        Linux (unknown)
    """
    Flashers.KNOWN['MCULink'] = {
        'type': 'flashers',
        'list_type': 'cli',
        'list_cmd': ['-c', 'PROBELIST'],
        'list_regex': r'Index = \s*\d+\s*Manufacturer = .*\s*Description = .*\s*Serial Number = (\S+)',
        'utility': str(f'{CLI_UTIL_PROBING_PATH}') if sys.platform == 'win32' else os.path.join('rltool')
    }

    SETTINGS = FlasherCommunicable.SETTINGS + ['script', 'package']

    def __init__(self, params):
        Flashers.__init__(self, params)
        self._verbosity = '2'
        self._timeout = 2
        FlasherCommunicable.__init__(self, params['interface'])

        if which(self._utility) is None:
            msg = f"Utility {self._utility} is not executable."
            self.logger.error(msg, extra=self.log_args)
            raise ValueError(msg)

        self._package = None
        self._script = None

        self.mark_taken(self)

    def __del__(self):
        FlasherCommunicable.release(self)

    def probe(self, interface, connections=None):
        interface['serial_number'] = self._serial_number
        return [interface]

    def _check_parameters(self):
        output = True

        if self._package is None:
            self.logger.error(
                msg=(
                    "In order to use the 'flash' or 'mass_erase' functionality, package has to be defined. "
                    "Define 'package' in config."
                ),
                extra=self.log_args
            )
            output = False
        elif self._script is None:
            self.logger.error(
                msg=(
                    "In order to use the 'flash' or 'mass_erase' functionality, script has to be defined. "
                    "Define 'script' in config. "
                    "Usual location: '<MCUXpresso_installation_path>/ide/binaries/Scripts/'."
                ),
                extra=self.log_args
            )
            output = False

        return output

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

        if not self._check_parameters():
            return None

        address = self._unify_address(address)

        # prepare command
        command = []
        command += ['--flash-load-exec', file]
        folder = ''
        if flashloader != "":
            folder, file = os.path.split(flashloader)
            command += ['--flash-driver', flashloader]
        if address != '':
            command += ['--load-base', address]
        command += ['--vendor', 'NXP', '-p', self._package]
        command += ['--ConnectScript', self._script]
        command += ['--no-packed', '--no-flash-hashing', '-CoreIndex=0', '-g', '--vc']
        command += ['-x', folder, '--flash-dir', folder]

        self.connect()

        process = run(self.__parse_connect() + command, stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            msg = (
                f'Return code: {process.returncode}, '
                'Unable to flash MCU memory{0}{1}'.format(os.linesep, process.stdout.read().decode())
            )
            self.logger.error(msg, extra=self.log_args)
            raise ConnectionError(msg)

        return process

    def mass_erase(self, timeout=None):
        # flash-mass-erase
        if timeout is None:
            timeout = self._timeout

        if not self._check_parameters():
            return None

        flashloader = self._flashloader

        command = ['--flash-mass-erase', ]
        command += ['-g', '--vc', '-CoreIndex=0']
        command += ['--vendor', 'NXP', '-p', self._package]
        command += ['--ConnectScript', self._script]
        folder = ''
        if flashloader != "":
            folder, file = os.path.split(flashloader)
            command += ['--flash-driver', flashloader]
            command += ['-x', folder, '--flash-dir', folder]

        self.connect()
        process = run(self.__parse_connect() + command, stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)
        if process.returncode != 0:
            msg = (
                f'Return code: {process.returncode}, '
                'Unable to perform mass erase{0}{1}'.format(os.linesep, process.stdout.read().decode())
            )
            self.logger.error(msg, extra=self.log_args)
            raise ConnectionError(msg)
        return process

    def erase_sector(self, sector, external_memory=False, timeout=None):
        raise NotImplementedError

    def write(self, address, data, timeout=None):
        tmp_file = tempfile.NamedTemporaryFile(mode='wb', suffix=".bin", delete=False)
        tmp_file.write(bytes(data))
        tmp_file.flush()

        # file need to be closed so CLI can open it
        tmp_file.close()

        # Perform flashing using crt_emu_cm_redlink, because redlinkserv could not be used #6672, #6816
        process = self.flash(file=tmp_file.name, address=address, timeout=timeout)

        os.remove(tmp_file.name)

        if process.returncode != 0:
            msg = (
                f'Return code: {process.returncode}, '
                'Unable to write MCU memory{0}{1}'.format(os.linesep, process.stdout.read().decode())
            )
            self.logger.error(msg, extra=self.log_args)
            raise ConnectionError(msg)
        return process

    def read(self, address, size, timeout=None):
        if timeout is None:
            timeout = self._timeout

        address = self._unify_address(address)

        inputs = (
            f'PROBEOPENBYSERIAL "{self._serial_number}"\n'
            'WIRESWDCONNECT THIS\n'
            f'MEMDUMP THIS {address} {size}\n'
            'EXIT'
        )

        command = [CLI_UTIL_SERVER_PATH, '--commandline']

        address = self._unify_address(address)
        self.connect()
        process = run(command, stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout, stdin=PIPE, input_=inputs)
        if process.returncode != 0:
            msg = (
                f'Return code: {process.returncode}, '
                'Unable to perform read from MCU memory{0}{1}'.format(os.linesep, process.stdout.read().decode())
            )
            self.logger.error(msg, extra=self.log_args)
            raise ConnectionError(msg)

        data = process.stdout.read().decode()

        data_regex = r"\w+:((\s+\w+)*\s*)\n"

        matches = re.finditer(data_regex, data, re.MULTILINE | re.IGNORECASE)

        out = []
        for match in matches:
            data = match.group(1).strip().split(" ")
            out.extend(int(i, 16) for i in data if i != '')

        return out

    def read_to_file(self, address, size, file, timeout=None):
        raise NotImplementedError

    def soft_reset(self, timeout=None):
        raise NotImplementedError

    def hard_reset(self, timeout=None):
        if timeout is None:
            timeout = 200

        if not self._check_parameters():
            return None

        # prepare command
        command = [CLI_UTIL_SERVER_PATH, '--commandline']

        inputs = (
            f'PROBEOPENBYSERIAL "{self._serial_number}"\n'
            'WIRESWDCONNECT THIS\n'
            'CMResetVectorCatchSet This\n'
            'CMSysResetReq This'
            'APList This\n'
            'CMInitApDp This\n'
            'CMResetVectorCatchClear This\n'
            'EXIT'
        )

        process = run(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout, input_=inputs)

        if process.returncode != 0:
            msg = (
                f'Return code: {process.returncode}, '
                'Unable to perform reset operation{0}{1}'.format(os.linesep, process.stdout.read().decode())
            )
            self.logger.error(msg, extra=self.log_args)
            raise ConnectionError(msg)

    def __parse_connect(self, *args):
        connect_args = [CLI_UTIL_USAGE_PATH]
        for arg in args:
            if arg != '':
                connect_args.append(arg)

        connect_args += ['-debug', self._verbosity]

        if self._serial_number != '':
            connect_args += ['--probeserial', self._serial_number]

        return connect_args

    def connect(self, timeout=None):
        pass

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

        return True

    def default_script(self, value):
        script = str(value)

        script_path = SCRIPT_PATH.format(script)

        if os.path.exists(script_path):
            self._script = script
        else:
            msg = f"Invalid path to MCU-Link connection script: '{script_path}' (script found in config: '{script}')."
            self.logger.error(msg, extra=self.log_args)
            return False

        return True

    def default_package(self, value):
        package = str(value)

        self._package = package

        return True

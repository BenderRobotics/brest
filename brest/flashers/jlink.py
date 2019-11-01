# -*- coding: utf-8 -*-
"""
    brest.flashers.JLink
    ~~~~~~~~~~~~~~~~~~~~

    This module implements JLink programmers

    :copyright: 2019 Bender Robotics
"""

import os
import re
import sys
import tempfile


from brest.flashers import Flashers
from brest.communication import FlasherCommunicable
from brest.log_subprocess import run, STDOUT, PIPE


class JLink(Flashers, FlasherCommunicable):
    """Segger programmer

    Derived from :class:`~brest.flashers.Flashers`, :class:`~brest.communication.FlasherCommunicable`

    :param params: Construction parameters
    :type  params: dict

    Supported models: PLUS, BASE, TRACER

    Supported CLI: JLink.exe

    Implicit interface definition::

        interface:
            type:       'flashers'
            list_type:  'usb'
            vid:        '1366'
            utility:    Windows - C:/ProgramFiles(x86)/SEGGER/JLink/JLink.exe
                        Linux   - Jlink
    """

    Flashers.KNOWN['JLink'] = {
        'type': 'flashers',
        'list_type': 'usb',
        'vid': '1366',
        'utility': os.path.join('C:/', 'Program Files (x86)', 'SEGGER', 'JLink',
                                'JLink.exe') if sys.platform == 'win32' else os.path.join('JLink')
    }

    def __init__(self, params):
        Flashers.__init__(self, params)
        FlasherCommunicable.__init__(self, params['interface'])

        self.mark_taken(self)

    def flash(self, file="", address="", flashloader="", timeout=None):
        if address == "":
            address = self._address
        if timeout is None:
            timeout = self._timeout

        if file is "":
            if self._file == "":
                self.logger.error("No file to flash", extra=self.log_args)
                return
            file = self._file

        if flashloader != '' or self._flashloader != '':
            self.logger.warning(
                'Flashloader is ignored for JLink, using flashloader in JLinkDevices.xml', extra=self.log_args)

        address = self._unify_address(address)

        tmp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        tmp_file.write("\n".join(['si ' + self._port, 'speed ' + self._frequency, 'r', 'h',
                                  'loadfile ' + file + ' ' + address, 'qc', '']))
        tmp_file.flush()

        # file need to be closed so CLI can open it
        tmp_file.close()

        process = run(self.__parse_connect(tmp_file.name), stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)

        os.remove(tmp_file.name)
        if process.returncode != 0:
            raise ConnectionError

    def write(self, address, data, timeout=None):
        if timeout is None:
            timeout = self._timeout

        raw_data = " ".join([hex(dat) for dat in data])

        address = self._unify_address(address)

        tmp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        tmp_file.write("\n".join(['si ' + self._port, 'speed ' + self._frequency, 'r', 'h',
                                  'w1 ' + address + ' ' + raw_data, 'qc', '']))
        tmp_file.flush()

        # file need to be closed so CLI can open it
        tmp_file.close()

        process = run(self.__parse_connect(tmp_file.name), stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)

        os.remove(tmp_file.name)
        if process.returncode != 0:
            raise ConnectionError

    def erase_sector(self, sector, timeout=None):
        raise NotImplementedError

    def mass_erase(self, timeout=None):
        if timeout is None:
            timeout = self._timeout

        tmp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        tmp_file.write('\n'.join(['si ' + self._port, 'speed ' + self._frequency,
                                  'r', 'h', 'exec EnableEraseAllFlashBanks',
                                  'erase', 'qc', '']))
        tmp_file.flush()
        tmp_file.close()

        process = run(self.__parse_connect(tmp_file.name), stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)

        os.remove(tmp_file.name)
        if process.returncode != 0:
            raise ConnectionError

    def read(self, address, size, timeout=None):
        address = self._unify_address(address)
        data = []
        matches = self.__raw_read(address, size, timeout)

        for match in matches:
            data.extend(match.group(1).split())
        return data

    def read_to_file(self, address, size, file, timeout=None):
        address = self._unify_address(address)

        with open(file, 'w') as file_handle:
            matches = self.__raw_read(address, size, timeout)
            for match in matches:
                file_handle.write(match.group(0) + '\n')
            file_handle.flush()

    def soft_reset(self, timeout=None):
        if timeout is None:
            timeout = self._timeout

        tmp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        tmp_file.write('\n'.join(['si ' + self._port, 'speed ' + self._frequency,
                                  'RSetType 8', 'r', 'qc', '']))
        tmp_file.flush()

        # file need to be closed so CLI can open it
        tmp_file.close()

        process = run(self.__parse_connect(tmp_file.name), stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)

        os.remove(tmp_file.name)
        if process.returncode != 0:
            raise ConnectionError
        raise NotImplementedError

    def hard_reset(self, timeout=None):
        if timeout is None:
            timeout = self._timeout

        tmp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        tmp_file.write('\n'.join(['si ' + self._port, 'speed ' + self._frequency, 'r', 'qc', '']))
        tmp_file.flush()
        # file need to be closed so CLI can open it
        tmp_file.close()

        process = run(self.__parse_connect(tmp_file.name), stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)

        os.remove(tmp_file.name)
        if process.returncode != 0:
            raise ConnectionError

    def __raw_read(self, address, size: int, timeout=None):
        if timeout is None:
            timeout = self._timeout

        tmp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        tmp_file.write('\n'.join(['si ' + self.port, 'speed ' + self.frequency, 'r', 'h',
                                  'mem8 ' + address + ' ' + str(hex(size)), 'qc', '']))
        tmp_file.flush()
        # file need to be closed so CLI can open it
        tmp_file.close()

        process = run(self.__parse_connect(tmp_file.name), stdout=PIPE, stderr=STDOUT,
                      log=self._log, timeout=timeout)

        os.remove(tmp_file.name)
        if process.returncode != 0:
            raise ConnectionError

        # read data from output log
        data_regex = r'[\dA-Fa-f]{7,12}\s*=\s*(([\dA-Fa-f]{2} ?)*)'
        raw_data = process.stdout.read().decode()

        return re.finditer(data_regex, raw_data, re.MULTILINE)

    def __parse_connect(self, command_file):
        return [self._utility, '-USB', self._serial_number,
                '-Device', self._device,
                '-CommandFile', command_file,
                '-ExitOnError', '1',
                ]

    def connect(self):
        tmp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
        tmp_file.write('\n'.join(['si ' + self._port, 'speed ' + self._frequency,
                                  'exec HideDeviceSelection 1', 'connect', 'qc', '']))
        tmp_file.flush()
        # file need to be closed so CLI can open it
        tmp_file.close()

        try:
            process = run(self.__parse_connect(tmp_file.name), stdout=PIPE, stderr=STDOUT,
                          timeout=2)
        except TimeoutError:
            raise ConnectionError
        finally:
            os.remove(tmp_file.name)

        if process.returncode != 0:
            raise ConnectionError

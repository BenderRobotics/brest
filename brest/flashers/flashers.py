import logging
import os
from shutil import which

from brest import Resource


class Flashers(Resource):
    """
    Base class for representing programmers
    """

    KNOWN = {}
    KNOWN['Flashers'] = {
        'type': 'flashers',
    }

    def __init__(self, params):
        Resource.__init__(self, params)
        self.logger = logging.getLogger('brest')

        self._log = 'none'
        self._quiet = True  # no progress bar

        self._device = ''
        self._reset = ""
        self._flashloader = ""

        self._mode = ""
        self._serial_number = ""
        self._port = "SWD"
        self._frequency = "4000"
        self._file = ""
        self._address = ""
        self._timeout = None

        if params.get('required'):
            if params['required'].get('utility'):
                self._utility = params['required']['utility']
                self._utility = os.path.normpath(self._utility)
            else:
                self._utility = params['interface']['utility']
        else:
            self._utility = params['interface']['utility']

        if not which(self._utility):
            self.logger.error("Utility is not executable", extra=self.log_args)
            raise ValueError

    @property
    def log(self):
        """
        Gets and sets type of logging [none, after, continous]
        """
        return self._log

    @log.setter
    def log(self, value):
        if value.lower() in ['none', 'after', 'continuous']:
            self._log = value.lower()
        else:
            raise TypeError

    @property
    def timeout(self):
        """
        Gets and set timeout
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError
        self._timeout = value

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, value):
        self._file = os.path.abspath(os.path.normpath(value))

    def flash(self, file="", address="", flashloader="", timeout=None):
        """
        Downloads file to MCU, optionable parameters will be set by config
        if not used (except skip_erase and verify).

        :param file: path to a file to flash
        :type file: str
        :param address: address where to flash image
        :type address: int
        :param flashloader: path to flashloader
        :type flashloader: str
        :param timeout: override class timeout
        :type timeout: float
        """
        pass

    def write(self, address, data, timeout=None):
        """
        Writes data to given address. Data needs to be in form of iterable hex values

        :param address: address where to flash image
        :type address: int
        :param data: data to flash
        :type data: iterable
        :param timeout: override class timeout
        :type timeout: float
        """
        pass

    def mass_erase(self, timeout=None):
        """
        Erase all sectors on MCU

        :param timeout: override class timeout
        :type timeout: float
        """
        pass

    def erase_sector(self, sector, timeout=None):
        """
        Erase given sector, sectors can be handled as number or interval -> [x, y] | (x, y)

        :param sector: sectors to erase
        :type sector: tuple, list, int
        :param timeout: override class timeout
        :type timeout: float
        """
        pass

    def read(self, address, size, timeout=None):
        """
        Reads size of bytes on address, output is driven by
        log and continuous variables.

        :param address: address where to flash image
        :type address: int
        :param size: ammount of data to read
        :type size: int
        :param timeout: override class timeout
        :type timeout: float
        """
        pass

    def read_to_file(self, address, size, file, timeout=None):
        """
        Reads size of bytes on address, ouput is disabled.

        :param address: address where to flash image
        :type address: int
        :param size: ammount of data to read
        :type size: int
        :param file: path to a file to flash
        :type file: str
        :param timeout: override class timeout
        :type timeout: float
        """
        pass

    def soft_reset(self, timeout=None):
        """
        Send reset command to MCU

        :param timeout: override class timeout
        :type timeout: float
        """
        pass

    def _unify_address(self, address):
        try:
            address = str(hex(address))
        except TypeError:
            address = str(address)

        return address

    def detect_model(self):
        """
        Dummy method to satisfy ResourceProvider
        """
        pass

    def required_flashloader(self, value):
        if value is None:
            return False

        self._flashloader = value
        return True

    def required_frequency(self, value):
        if value is None:
            return False

        try:
            int(value)
        except ValueError:
            self.logger.error('Invalid frequency value', extra=self.log_args)
            return False

        self._frequency = value
        return True

    def required_log(self, value):
        value = str(value)
        try:
            self.log = value
            return True
        except TypeError:
            return False

    def required_file(self, value):
        if value is None:
            return False

        self._file = value
        return True

    def required_port(self, value):
        value = str(value)
        if value.lower() in ['swd', 'jtag']:
            self._port = value.upper()
            return True

        self.logger.error("Invalid value of port", extra=self.log_args)
        return False

    def required_device(self, value):
        if not isinstance(value, str):
            self.logger.error('Invalid device type', extra=self.log_args)
            return False

        if value is None or value == '':
            self.logger.error('Specify device', extra=self.log_args)
            return False

        self._device = value
        return True

    def required_address(self, value):
        self._address = value
        return True

    def required_utility(self, value):
        return True

    def required_timeout(self, value):
        try:
            self.timeout = value
            return True
        except TypeError:
            return False

    def __del__(self):
        self.unmark_taken(self)

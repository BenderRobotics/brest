#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.multimeters.multicomp
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements Multicomp pro MP730889 programmable multimeter.

    :copyright: 2024 Bender Robotics
"""
from enum import Enum

from brest.multimeters import Multimeters
from brest.communication import SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand


class Multicomp(Multimeters, SCPICommunicable):
    """
    Multicomp Pro MP73xxxx series programmable tabletop multimeter

    Derived from :class:`~brest.multimeters.Multimeters`, :class:`~brest.communication.SCPICommunicable`

    :param params: Construction parameters
    :type  params: dict

    Supported models: Multicomp Pro MP730889

    Implicit interface definition::

        interface:
            type:       'serial'
            timeout:    0.1
            vid:        0x1A86
            pid:        0x7523
            baudrate:   115200

    This resource tries to disable itself upon destruction. To change this behavior, refer to
    :attr:`~brest.Resource.disable_on_destruct`.
    """

    ALIAS = 'MP73'

    #: Implicit interface definition
    Multimeters.KNOWN['Multicomp'] = {
        'type': 'serial',
        'timeout': 0.5,
        'vid': 0x1A86,
        'pid': 0x7523,
        'baudrate': 115200,
    }

    Models = [
        Multimeters.Model('Multicomp Pro MP730889', 65, 20, 1000, True, Multimeters.Kind.PROGRAMMABLE),
    ]

    class Commands():
        """
        Available commands
        """
        MEASURE = SCPIQueryCommand('MEAS')  # Returns the curent measured value
        MEASURE_2 = SCPIQueryCommand('MEAS2')  # Returns the 2nd function (FREQ in AC mode)
        RATE_FAST = SCPICommand('RATE F')  # Sets sampling speed to the highest setting
        GET_MODE = SCPIQueryCommand('FUNC')  # Returns the current function (measurement mode) of the device
        GET_INFO = SCPIQueryCommand('*IDN')  # Returns basic info about the device
        GET_RANGE = SCPIQueryCommand('RANGE')
        GET_AUTO = SCPIQueryCommand('AUTO')
        # Voltage DC range
        SET_VOLT_RANGE_DC_AUTO = SCPIValueCommand('CONF:VOLT:DC', delimiter=' ', value='AUTO')
        SET_VOLT_RANGE_DC_50V = SCPIValueCommand('CONF:VOLT:DC', delimiter=' ', value='50')
        SET_VOLT_RANGE_DC_5V = SCPIValueCommand('CONF:VOLT:DC', delimiter=' ', value='5')
        SET_VOLT_RANGE_DC_500MV = SCPIValueCommand('CONF:VOLT:DC', delimiter=' ', value='500E-3')
        SET_VOLT_RANGE_DC_50MV = SCPIValueCommand('CONF:VOLT:DC', delimiter=' ', value='50E-3')
        # Voltage AC range
        SET_VOLT_RANGE_AC_AUTO = SCPIValueCommand('CONF:VOLT:AC', delimiter=' ', value='AUTO')
        SET_VOLT_RANGE_AC_750V = SCPIValueCommand('CONF:VOLT:AC', delimiter=' ', value='750')
        SET_VOLT_RANGE_AC_500V = SCPIValueCommand('CONF:VOLT:AC', delimiter=' ', value='500')
        SET_VOLT_RANGE_AC_50V = SCPIValueCommand('CONF:VOLT:AC', delimiter=' ', value='50')
        SET_VOLT_RANGE_AC_5V = SCPIValueCommand('CONF:VOLT:AC', delimiter=' ', value='5')
        SET_VOLT_RANGE_AC_500MV = SCPIValueCommand('CONF:VOLT:AC', delimiter=' ', value='500E-3')
        # Current DC range
        SET_CURR_RANGE_DC_AUTO = SCPIValueCommand('CONF:CURR:DC', delimiter=' ', value='AUTO')
        SET_CURR_RANGE_DC_5MA = SCPIValueCommand('CONF:CURR:DC', delimiter=' ', value='5E-3')
        SET_CURR_RANGE_DC_50MA = SCPIValueCommand('CONF:CURR:DC', delimiter=' ', value='50E-3')
        SET_CURR_RANGE_DC_500MA = SCPIValueCommand('CONF:CURR:DC', delimiter=' ', value='500E-3')
        SET_CURR_RANGE_DC_5A = SCPIValueCommand('CONF:CURR:DC', delimiter=' ', value='5')
        SET_CURR_RANGE_DC_10A = SCPIValueCommand('CONF:CURR:DC', delimiter=' ', value='10')
        # Current AC range
        SET_CURR_RANGE_AC_AUTO = SCPIValueCommand('CONF:CURR:AC', delimiter=' ', value='AUTO')
        SET_CURR_RANGE_AC_500UA = SCPIValueCommand('CONF:CURR:AC', delimiter=' ', value='500E-6')
        SET_CURR_RANGE_AC_5MA = SCPIValueCommand('CONF:CURR:AC', delimiter=' ', value='5E-3')
        SET_CURR_RANGE_AC_50MA = SCPIValueCommand('CONF:CURR:AC', delimiter=' ', value='50E-3')
        SET_CURR_RANGE_AC_500MA = SCPIValueCommand('CONF:CURR:AC', delimiter=' ', value='500E-3')
        SET_CURR_RANGE_AC_5A = SCPIValueCommand('CONF:CURR:AC', delimiter=' ', value='5')
        SET_CURR_RANGE_AC_10A = SCPIValueCommand('CONF:CURR:AC', delimiter=' ', value='10')
        # Resistance
        SET_RES_RANGE_AUTO = SCPIValueCommand('CONF:RES', delimiter=' ', value='AUTO')
        SET_RES_RANGE_500R = SCPIValueCommand('CONF:RES', delimiter=' ', value='500')
        SET_RES_RANGE_5KR = SCPIValueCommand('CONF:RES', delimiter=' ', value='5E3')
        SET_RES_RANGE_50KR = SCPIValueCommand('CONF:RES', delimiter=' ', value='50E3')
        SET_RES_RANGE_500KR = SCPIValueCommand('CONF:RES', delimiter=' ', value='500E3')
        SET_RES_RANGE_5MR = SCPIValueCommand('CONF:RES', delimiter=' ', value='5E6')
        SET_RES_RANGE_50MR = SCPIValueCommand('CONF:RES', delimiter=' ', value='50E6')
        # Capacitance
        SET_CAP_RANGE_AUTO = SCPIValueCommand('CONF:CAP', delimiter=' ', value='AUTO')
        SET_CAP_RANGE_50NF = SCPIValueCommand('CONF:CAP', delimiter=' ', value='50E-9')
        SET_CAP_RANGE_500NF = SCPIValueCommand('CONF:CAP', delimiter=' ', value='500E-9')
        SET_CAP_RANGE_5UF = SCPIValueCommand('CONF:CAP', delimiter=' ', value='5E-6')
        SET_CAP_RANGE_50UF = SCPIValueCommand('CONF:CAP', delimiter=' ', value='50E-6')
        SET_CAP_RANGE_500UF = SCPIValueCommand('CONF:CAP', delimiter=' ', value='500E-6')
        SET_CAP_RANGE_5MF = SCPIValueCommand('CONF:CAP', delimiter=' ', value='5E-3')
        SET_CAP_RANGE_50MF = SCPIValueCommand('CONF:CAP', delimiter=' ', value='50E-3')
        # Frequency
        SET_MODE_FREQ = SCPICommand('CONF:FREQ')
        # Temperature sensors
        SET_TEMP_KITS90 = SCPIValueCommand('CONF:TEMP:RTD', delimiter=' ', value='KITS90')
        SET_TEMP_PT100 = SCPIValueCommand('CONF:TEMP:RTD', delimiter=' ', value='PT100')
        # Temperature units
        SET_TEMP_UNIT_C = SCPIValueCommand('TEMP:RTD:UNIT', delimiter=' ', value='C')
        SET_TEMP_UNIT_F = SCPIValueCommand('TEMP:RTD:UNIT', delimiter=' ', value='F')
        SET_TEMP_UNIT_K = SCPIValueCommand('TEMP:RTD:UNIT', delimiter=' ', value='K')

    class Ranges(Enum):
        """
        Available ranges to be used in setting specific modes of the device.
        """
        # DC Voltage
        DC_50MV = 'DC_50MV'
        DC_500MV = 'DC_500MV'
        DC_5V = 'DC_5V'
        DC_50V = 'DC_50V'
        DC_VOLT_AUTO = 'DC_VOLT_AUTO'
        # DC Current
        DC_5MA = 'DC_5MA'
        DC_50MA = 'DC_50MA'
        DC_500MA = 'DC_500MA'
        DC_5A = 'DC_5A'
        DC_10A = 'DC_10A'
        DC_CURR_AUTO = 'DC_CURR_AUTO'
        # AC Voltage
        AC_500MV = 'AC_500MV'
        AC_5V = 'AC_5V'
        AC_50V = 'AC_50V'
        AC_500V = 'AC_500V'
        AC_750V = 'AC_750V'
        AC_VOLT_AUTO = 'AC_VOLT_AUTO'
        # AC Current
        AC_500UA = 'AC_500UA'
        AC_5MA = 'AC_5MA'
        AC_50MA = 'AC_50MA'
        AC_500MA = 'AC_500MA'
        AC_5A = 'AC_5A'
        AC_10A = 'AC_10A'
        AC_CURR_AUTO = 'AC_CURR_AUTO'
        # Resistance
        RES_500R = 'RES_500R'
        RES_5KR = 'RES_5KR'
        RES_50KR = 'RES_50KR'
        RES_500KR = 'RES_500KR'
        RES_5MR = 'RES_5MR'
        RES_50MR = 'RES_50MR'
        RES_AUTO = 'RES_AUTO'
        # Capacitance
        CAP_50NF = 'CAP_50NF'
        CAP_500NF = 'CAP_500NF'
        CAP_5UF = 'CAP_5UF'
        CAP_50UF = 'CAP_50UF'
        CAP_500UF = 'CAP_500UF'
        CAP_5MF = 'CAP_5MF'
        CAP_50MF = 'CAP_50MF'
        CAP_AUTO = 'CAP_AUTO'

        FREQ_HZ = 'FREQ_HZ'

    class Units(Enum):
        """
        Available units user can specify in measuring methods
        """
        UNIT_MV = 'UNIT_MV'  # miliVolts
        UNIT_V = 'UNIT_V'  # Volts

        UNIT_UA = 'UNIT_UA'  # microAmps
        UNIT_MA = 'UNIT_MA'  # miliAmps
        UNIT_A = 'UNIT_A'  # Amps

        UNIT_NF = 'UNIT_NF'  # nanoFarads
        UNIT_UF = 'UNIT_UF'  # microFarads
        UNIT_MF = 'UNIT_MF'  # miliFarads
        UNIT_M = 'UNIT_M'  # Farads

        UNIT_R = 'UNIT_R'  # Ohms
        UNIT_KR = 'UNIT_KR'  # kiloOhms
        UNIT_MR = 'UNIT_MR'  # MegaOhms

        UNIT_C = 'UNIT_C'  # degrees Celsius
        UNIT_K = 'UNIT_K'  # Kelvins
        UNIT_F = 'UNIT_F'  # degrees Fahrenheit

        UNIT_HZ = 'UNIT_HZ'  # Hz

    class Modes(Enum):
        """
        Available measurement modes of the device
        """
        VOLT = 0
        CURR = 1
        VOLT_AC = 2
        CURR_AC = 3
        RES = 4
        CAP = 5
        TEMP = 6
        FREQ = 7

    class TempSensors(Enum):
        """
        Available temperature sensor types
        """
        KITS90 = 1
        PT100 = 2

    def __init__(self, params):
        Multimeters.__init__(self, params)
        SCPICommunicable.__init__(self, params['interface'])

        self.determine_suffix(self.Commands.GET_INFO)

        self.VOLTAGE_UNITS = [self.Units.UNIT_MV, self.Units.UNIT_V]
        self.CURRENT_UNITS = [self.Units.UNIT_UA, self.Units.UNIT_MA, self.Units.UNIT_A]
        self.RESISTANCE_UNITS = [self.Units.UNIT_R, self.Units.UNIT_KR, self.Units.UNIT_MR]
        self.TEMPERATURE_UNITS = [self.Units.UNIT_C, self.Units.UNIT_K]

        # Collecting possible device modes from the Modes enum class
        self.possible_modes = [mode.name for mode in self.Modes]

        self.mode = None

    def wait_for_response(self):
        res = 0
        n = 0
        # Waiting for the multimeter to start measuring
        while res == 0 and n < 3:
            res = self.transceive(self.Commands.MEASURE)
            n += 1

    def _detect_mode(self) -> Modes:
        """
        This method asks the device for the current mode setting. It then compares it to the list of possible modes
        (collected from the Modes enum class) and returns is.
        """
        mode_received = self.transceive(self.Commands.GET_MODE)
        successful = False
        for mode in self.Modes:
            if mode.name == mode_received.replace(':', '_').strip(' "\r\n'):
                self.mode = mode
                successful = True
                break
        if not successful:
            raise ValueError(f"Mode received in an incorrect format. Received message: {mode_received}")
        return self.mode

    def is_mode(self, mode) -> bool:
        if isinstance(mode, self.Modes):
            current_mode = self._detect_mode()
            if mode == current_mode:
                return True
            else:
                return False
        else:
            self.logger.error(f"Mode has to be of type multicomp.Modes, not {type(mode)}", extra=self.log_args)
            return False

    def get_info(self):
        device_info = self.transceive(self.Commands.GET_INFO).replace(',', ', ').strip('\r\n')
        mode = self.transceive(self.Commands.GET_MODE).strip('\r\n')
        range = self.transceive(self.Commands.GET_RANGE).strip('\r\n')
        auto = self.transceive(self.Commands.GET_AUTO).strip('\r\n')
        response = {"Device information": device_info, "Mode": mode, "Range": range, "Auto": auto}
        return response

    def get_mode(self):
        mode = self.transceive(self.Commands.GET_MODE).strip('\r\n')
        return mode

    def get_range(self):
        # TODO: Fix problem with reading:
        #   Temp (returns sensor type),
        #   Resistance (utf-8 cant decode received message),
        #   Diode (receives "DIOD" as range)
        range_rec = self.transceive(self.Commands.GET_RANGE).strip('\r\n').replace(' ', '').upper()
        for range in self.Ranges:
            if range_rec in range.value:
                result = range
                break
            else:
                result = None
        return range_rec

    def detect_model(self):
        response = self.transceive(self.Commands.GET_INFO)
 
        if response and isinstance(response, str):
            split_response = response.split(',')
            if len(split_response) >= 3:
                series = split_response[0]
                model_str = split_response[1]
                serial_number = split_response[2]

                for model in self.Models:
                    if model_str.lower() in model.idn.lower():
                        self._apply_model(model)
                        self.logger.info(f'Detected model {series} {model_str}', extra=self.log_args)
                        return

        raise LookupError('Unable to detect a valid Multicomp multimeter model.')

    def set_mode_voltage_dc(self, range=Ranges.DC_5V) -> None:
        """
        Sends a command to set the mode to voltage DC with specified range.

        :param range: Measuring range of the multimeter
        :type  params: Multicomp.Modes
        """
        if range == self.Ranges.DC_50MV:
            self.transceive(self.Commands.SET_VOLT_RANGE_DC_50MV)
        elif range == self.Ranges.DC_500MV:
            self.transceive(self.Commands.SET_VOLT_RANGE_DC_500MV)
        elif range == self.Ranges.DC_5V:
            self.transceive(self.Commands.SET_VOLT_RANGE_DC_5V)
        elif range == self.Ranges.DC_50V:
            self.transceive(self.Commands.SET_VOLT_RANGE_DC_50V)
        elif range == self.Ranges.DC_VOLT_AUTO:
            self.transceive(self.Commands.SET_VOLT_RANGE_DC_AUTO)
        else:
            raise Exception(f"Incorrect voltage range was received: {range}")
        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()
        if self.is_mode(self.Modes.VOLT):
            self.mode = self.Modes.VOLT
            self.logger.info(f"Measurement mode has been set to Voltage DC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to VOLTAGE DC was not successful", extra=self.log_args)

    def set_mode_voltage_ac(self, range=Ranges.AC_5V) -> None:
        """
        Sends a command to set the mode to voltage AC with specified range.

        :param range: Measuring range of the multimeter
        :type  params: Multicomp.Modes
        """
        if range == self.Ranges.AC_500MV:
            self.transceive(self.Commands.SET_VOLT_RANGE_AC_500MV)
        elif range == self.Ranges.AC_5V:
            self.transceive(self.Commands.SET_VOLT_RANGE_AC_5V)
        elif range == self.Ranges.AC_50V:
            self.transceive(self.Commands.SET_VOLT_RANGE_AC_50V)
        elif range == self.Ranges.AC_500V:
            self.transceive(self.Commands.SET_VOLT_RANGE_AC_500V)
        elif range == self.Ranges.AC_750V:
            self.transceive(self.Commands.SET_VOLT_RANGE_AC_750V)
        elif range == self.Ranges.AC_VOLT_AUTO:
            self.transceive(self.Commands.SET_VOLT_RANGE_AC_AUTO)
        else:
            raise Exception(f"Incorrect voltage range was received: {range}")
        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()
        if self.is_mode(self.Modes.VOLT_AC):
            self.mode = self.Modes.VOLT_AC
            self.logger.info(f"Measurement mode has been set to Voltage AC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to VOLTAGE AC was not successful", extra=self.log_args)

    def set_mode_current_dc(self, range=Ranges.DC_10A) -> None:
        """
        Sends a command to set the mode to voltage DC with specified range.

        :param range: Measuring range of the multimeter
        :type  params: Multicomp.Modes
        """
        if range == self.Ranges.DC_5MA:
            self.transceive(self.Commands.SET_CURR_RANGE_DC_5MA)
        elif range == self.Ranges.DC_50MA:
            self.transceive(self.Commands.SET_CURR_RANGE_DC_50MA)
        elif range == self.Ranges.DC_500MA:
            self.transceive(self.Commands.SET_CURR_RANGE_DC_500MA)
        elif range == self.Ranges.DC_5A:
            self.transceive(self.Commands.SET_CURR_RANGE_DC_5A)
        elif range == self.Ranges.DC_10A:
            self.transceive(self.Commands.SET_CURR_RANGE_DC_10A)
        elif range == self.Ranges.DC_CURR_AUTO:
            self.transceive(self.Commands.SET_CURR_RANGE_DC_AUTO)
        else:
            raise Exception(f"Incorrect current range was received: {range}")
        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()
        if self.is_mode(self.Modes.CURR):
            self.mode = self.Modes.CURR
            self.logger.info(f"Measurement mode has been set to Current DC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to CURRENT DC was not successful", extra=self.log_args)

    def set_mode_current_ac(self, range=Ranges.AC_10A) -> None:
        """
        Sends a command to set the mode to voltage DC with specified range.

        :param range: Measuring range of the multimeter
        :type  params: Multicomp.Modes
        """
        if range == self.Ranges.AC_500UA:
            self.transceive(self.Commands.SET_CURR_RANGE_AC_500UA)
        elif range == self.Ranges.AC_5MA:
            self.transceive(self.Commands.SET_CURR_RANGE_AC_5MA)
        elif range == self.Ranges.AC_50MA:
            self.transceive(self.Commands.SET_CURR_RANGE_AC_50MA)
        elif range == self.Ranges.AC_500MA:
            self.transceive(self.Commands.SET_CURR_RANGE_AC_500MA)
        elif range == self.Ranges.AC_5A:
            self.transceive(self.Commands.SET_CURR_RANGE_AC_5A)
        elif range == self.Ranges.AC_10A:
            self.transceive(self.Commands.SET_CURR_RANGE_AC_10A)
        elif range == self.Ranges.AC_CURR_AUTO:
            self.transceive(self.Commands.SET_CURR_RANGE_AC_AUTO)
        else:
            raise Exception(f"Incorrect current range was received: {range}")
        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()
        if self.is_mode(self.Modes.CURR_AC):
            self.mode = self.Modes.CURR_AC
            self.logger.info(f"Measurement mode has been set to Current AC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to CURRENT AC was not successful", extra=self.log_args)

    def set_mode_temperature(self, sensor_type=TempSensors.KITS90, unit=Units.UNIT_C) -> None:
        """
        Sends a command to set the mode to temperature using specified type of sensor.

        :param sensor_type: defaults to TempSensors.KITS90
        :type  params: self.TempSensors
        """
        if sensor_type == self.TempSensors.KITS90:
            self.transceive(self.Commands.SET_TEMP_KITS90)
        elif sensor_type == self.TempSensors.PT100:
            self.transceive(self.Commands.SET_TEMP_PT100)
        else:
            self.logger.error(f"Incorrect temperature sensor type was received: {sensor_type}", extra=self.log_args)

        if unit == self.Units.UNIT_C:
            self.transceive(self.Commands.SET_TEMP_UNIT_C)
        elif unit == self.Units.UNIT_F:
            self.transceive(self.Commands.SET_TEMP_UNIT_F)
        elif unit == self.Units.UNIT_K:
            self.transceive(self.Commands.SET_TEMP_UNIT_K)
        else:
            raise Exception(f"Incorrect temperature range was received: {range}")

        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()
        if self.is_mode(self.Modes.TEMP):
            self.mode = self.Modes.TEMP
            self.logger.info(
                msg=f"Measurement mode has been set to Temperature, sensor: {sensor_type.name}",
                extra=self.log_args
            )
        else:
            self.logger.error(f"Setting the mode to TEMPERATURE was not successful", extra=self.log_args)

    def set_mode_resistance(self, range=Ranges.RES_50MR):
        """
        Sends a command to set the mode to resistance with specified range.

        :param range: Measuring range of the multimeter
        :type  params: Multicomp.Modes
        """
        if range == self.Ranges.RES_500R:
            self.transceive(self.Commands.SET_RES_RANGE_500R)
        elif range == self.Ranges.RES_5KR:
            self.transceive(self.Commands.SET_RES_RANGE_5KR)
        elif range == self.Ranges.RES_50KR:
            self.transceive(self.Commands.SET_RES_RANGE_50KR)
        elif range == self.Ranges.RES_500KR:
            self.transceive(self.Commands.SET_RES_RANGE_500KR)
        elif range == self.Ranges.RES_5MR:
            self.transceive(self.Commands.SET_RES_RANGE_5MR)
        elif range == self.Ranges.RES_50MR:
            self.transceive(self.Commands.SET_RES_RANGE_50MR)
        elif range == self.Ranges.RES_AUTO:
            self.transceive(self.Commands.SET_RES_RANGE_AUTO)
        else:
            raise Exception(f"Incorrect resistance range was received: {range}")
        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()
        if self.is_mode(self.Modes.RES):
            self.mode = self.Modes.RES
            self.logger.info(f"Measurement mode has been set to Resistance, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to RESISTANCE was not successful", extra=self.log_args)

    def set_mode_capacitance(self, range=Ranges.CAP_50MF):
        """
        Sends a command to set the mode to capacitance with specified range.

        :param range: Measuring range of the multimeter
        :type  params: Multicomp.Modes
        """
        if range == self.Ranges.CAP_50NF:
            self.transceive(self.Commands.SET_CAP_RANGE_50NF)
        elif range == self.Ranges.CAP_500NF:
            self.transceive(self.Commands.SET_CAP_RANGE_500NF)
        elif range == self.Ranges.CAP_5UF:
            self.transceive(self.Commands.SET_CAP_RANGE_5UF)
        elif range == self.Ranges.CAP_50UF:
            self.transceive(self.Commands.SET_CAP_RANGE_50UF)
        elif range == self.Ranges.CAP_500UF:
            self.transceive(self.Commands.SET_CAP_RANGE_500UF)
        elif range == self.Ranges.CAP_5MF:
            self.transceive(self.Commands.SET_CAP_RANGE_5MF)
        elif range == self.Ranges.CAP_50MF:
            self.transceive(self.Commands.SET_CAP_RANGE_50MF)
        elif range == self.Ranges.CAP_AUTO:
            self.transceive(self.Commands.SET_CAP_RANGE_AUTO)
        else:
            raise Exception(f"Incorrect capacitance range was received: {range}")
        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()
        if self.is_mode(self.Modes.CAP):
            self.mode = self.Modes.CAP
            self.logger.info(f"Measurement mode has been set to Capacitance, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to CAPACITANCE was not successful", extra=self.log_args)

    def set_mode_frequency(self):
        """
        Sends a command to set the mode to frequency.
        """
        self.transceive(self.Commands.SET_MODE_FREQ)
        self.transceive(self.Commands.RATE_FAST)
        self.wait_for_response()

        if self.is_mode(self.Modes.FREQ):
            self.mode = self.Modes.FREQ
            self.logger.info(f"Measurement mode has been set to Frequency", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to FREQUENCY was not successful", extra=self.log_args)

    def measure_temperature(self) -> float:
        """
        Sends a query command to get a measurement of temperature.
        Returns measured temperature.
        """
        if self.mode != self.Modes.TEMP:
            self.logger.error(
                msg=f"Device is not in the correct state - TEMPERATURE [Modes.TEMP]. Current mode: {self.mode}",
                extra=self.log_args
            )
            return None
        received = self.transceive(self.Commands.MEASURE).strip('\r\n')
        try:
            result = float(received)
        except ValueError:
            self.logger.error(
                msg=f"Incorrect value received from the device. Couldn't convert {received} to `float`",
                extra=self.log_args,
            )
            result = None
        return result

    def measure_frequency(self) -> float:
        """
        Sends a query command to get a measurement of Frequency.
        Returns measured frequency in Hz.
        """
        if self.mode != self.Modes.FREQ:
            self.logger.error(
                msg=f"Device is not in the correct state - FREQUENCY [Modes.FREQ]. Current mode: {self.mode}",
                extra=self.log_args
            )
            return None

        received = self.transceive(self.Commands.MEASURE).strip('\r\n')
        try:
            result = float(received)
        except ValueError:
            self.logger.error(
                msg=f"Incorrect value received from the device. Couldn't convert {received} to `float`",
                extra=self.log_args,
            )
            result = None
        return result

    def measure_capacitance(self, unit=Units.UNIT_MF) -> float:
        """
        Sends a query command to get a measurement of Capacitance.
        Returns measured capacitance in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        if self.mode != self.Modes.CAP:
            self.logger.error(
                msg=f"Device is not in the correct state - CAPACITANCE [Modes.CAP]. Current mode: {self.mode}",
                extra=self.log_args
            )
            return None
        multiplier = 1
        if unit == self.Units.UNIT_MF:
            multiplier = 1e3
        elif unit == self.Units.UNIT_UF:
            multiplier = 1e6
        elif unit == self.Units.UNIT_NF:
            multiplier = 1e9
        else:
            raise ValueError(f"Incorrect unit received for Capacitance: {unit}")

        received = self.transceive(self.Commands.MEASURE).strip('\r\n')
        try:
            result = float(received) * multiplier
        except ValueError:
            self.logger.error(
                msg=f"Incorrect value received from the device. Couldn't convert {received} to `float`",
                extra=self.log_args,
            )
            result = None
        return result

    def measure_resistance(self, unit=Units.UNIT_R) -> float:
        """
        Sends a query command to get a measurement of Resistance.
        Returns measured resistance in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        if self.mode != self.Modes.RES:
            self.logger.error(
                msg=f"Device is not in the correct state - RESISTANCE [Modes.RES]. Current mode: {self.mode}",
                extra=self.log_args
            )
            return None
        multiplier = 1
        if unit == self.Units.UNIT_R:
            # default unit
            pass
        elif unit == self.Units.UNIT_KR:
            multiplier = 1e-3
        elif unit == self.Units.UNIT_MR:
            multiplier = 1e-6
        else:
            raise ValueError(f"Incorrect unit received for Resistance: {unit}")

        received = self.transceive(self.Commands.MEASURE).strip('\r\n')
        try:
            result = float(received)*multiplier
        except ValueError:
            self.logger.error(
                msg=f"Incorrect value received from the device. Couldn't convert {received} to `float`",
                extra=self.log_args
            )
            result = None
        return result

    def measure_voltage(self, unit=Units.UNIT_V) -> float:
        """
        Sends a query command to get a measurement of Voltage.
        Base function for both DC and AC voltage measurement
        Returns measured voltage in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        multiplier = 1
        if unit not in self.VOLTAGE_UNITS:
            raise ValueError(f'Unit {unit} is not supported (part of VOLTAGE_UNITS)')

        if unit == self.Units.UNIT_V:
            # default unit
            pass
        elif unit == self.Units.UNIT_MV:
            multiplier = 1e3

        received = self.transceive(self.Commands.MEASURE).strip('\r\n')
        try:
            result = float(received) * multiplier
        except Exception as ex:
            self.logger.error(
                msg=f"Incorrect value received from the device. Couldn't convert {received} to `float`",
                extra=self.log_args,
                exc_info=True
            )
            result = None
        return result

    def measure_current(self, unit=Units.UNIT_A) -> float:
        """
        Sends a query command to get a measurement of Current.
        Base function for both DC and AC current measurement
        Returns measured current in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        multiplier = 1
        if unit not in self.CURRENT_UNITS:
            raise ValueError(f'Unit {unit} is not supported (part of CURRENT_UNITS)')
        if unit == self.Units.UNIT_A:
            # default unit
            pass
        elif unit == self.Units.UNIT_MA:
            multiplier = 1e3
        elif unit == self.Units.UNIT_UA:
            multiplier = 1e6
        else:
            raise ValueError(f"Incorrect unit received for Current: {unit}")

        received = self.transceive(self.Commands.MEASURE).strip('\r\n')
        try:
            result = float(received) * multiplier
        except Exception as ex:
            self.logger.error(
                msg=f"Incorrect value received from the device. Couldn't convert {received} to `float`",
                extra=self.log_args,
                exc_info=True
            )
            result = None
        return result

    def measure_voltage_dc(self, unit=Units.UNIT_V) -> float:
        """
        Checks the correct mode and calls the measure_voltage() method.
        Returns measured voltage in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        if self.mode == self.Modes.VOLT:
            result = self.measure_voltage(unit)
        else:
            self.logger.error(
                msg=f"Device is not in the correct state - VOLTAGE DC [Modes.VOLT]. Current mode: {self.mode}",
                extra=self.log_args
            )
            result = None
        return result

    def measure_voltage_ac(self, unit=Units.UNIT_V) -> float:
        """
        Checks the correct mode and calls the measure_voltage() method.
        Returns measured voltage in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        if self.mode == self.Modes.VOLT_AC:
            result = self.measure_voltage(unit)
        else:
            self.logger.error(
                msg=f"Device is not in the correct state - VOLTAGE AC [Modes.VOLT_AC]. Current mode: {self.mode}",
                extra=self.log_args
            )
            result = None
        return result

    def measure_current_dc(self, unit=Units.UNIT_A) -> float:
        """
        Checks the correct mode and calls the measure_current() method.
        Returns measured current in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        if self.mode == self.Modes.CURR:
            result = self.measure_current(unit)
        else:
            self.logger.error(
                msg=f"Device is not in the correct state - CURRENT DC [Modes.CURR]. Current mode: {self.mode}",
                extra=self.log_args
            )
            result = None
        return result

    def measure_current_ac(self, unit=Units.UNIT_A) -> float:
        """
        Checks the correct mode and calls the measure_current() method.
        Returns measured current in the specified unit.

        :param unit: The output unit
        :type  params: Multicomp.Units
        """
        if self.mode == self.Modes.CURR_AC:
            result = self.measure_current(unit)
        else:
            self.logger.error(
                msg=f"Device is not in the correct state - CURRENT AC [Modes.CURR_AC]. Current mode: {self.mode}",
                extra=self.log_args
            )
            result = None
        return result

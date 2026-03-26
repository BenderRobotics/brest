#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.multimeters.MP71
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements Multicomp pro MP71xxxx programmable multimeter.

    :copyright: 2026 Bender Robotics
"""
from enum import Enum

from brest.multimeters import Multimeters
from brest.communication import SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand


class MP71(Multimeters, SCPICommunicable):
    """
    Multicomp Pro MP71xxxx series programmable tabletop multimeter

    Derived from :class:`~brest.multimeters.Multimeters`, :class:`~brest.communication.SCPICommunicable`

    :param params: Construction parameters
    :type  params: dict

    Supported models: Multicomp Pro MP711132

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

    #: Implicit interface definition
    Multimeters.KNOWN['MP71'] = {
        'type': 'serial',
        'timeout': 0.5,
        'vid': 0x1A86,
        'pid': 0x7523,
        'baudrate': 115200,
    }

    Models = [
        Multimeters.Model('Multicomp Pro MP711132', 65, 40, 1000, True, Multimeters.Kind.PROGRAMMABLE),
    ]

    class Commands():
        """
        Available commands according to SPM Series programming manual
        """
        MEASURE = SCPIQueryCommand('CONF')  # Returns mode and value
        GET_MODE = SCPIQueryCommand('CONF:ALL') # Use CONF as it's more reliable for mode + status
        GET_INFO = SCPIQueryCommand('*IDN')  # Returns basic info about the device
        
        # Mode switching
        SET_MODE_VOLT_DC = SCPICommand('FUNC:VOLT:DC')
        SET_MODE_VOLT_AC = SCPICommand('FUNC:VOLT:AC')
        SET_MODE_CURR_DC = SCPICommand('FUNC:CURR:DC')
        SET_MODE_CURR_AC = SCPICommand('FUNC:CURR:AC')
        SET_MODE_RES = SCPICommand('FUNC:RES')
        SET_MODE_CAP = SCPICommand('FUNC:CAP')
        SET_MODE_DIOD = SCPICommand('FUNC:DIOD')
        SET_MODE_CONT = SCPICommand('FUNC:CONT')

        # Range and Auto
        SET_VOLT_DC_RANGE = SCPIValueCommand('VOLT:DC:RANG', delimiter=' ')
        SET_VOLT_AC_RANGE = SCPIValueCommand('VOLT:AC:RANG', delimiter=' ')
        SET_CURR_DC_RANGE = SCPIValueCommand('CURR:DC:RANG', delimiter=' ')
        SET_CURR_AC_RANGE = SCPIValueCommand('CURR:AC:RANG', delimiter=' ')
        SET_CAP_RANGE = SCPIValueCommand('CAP:RANG', delimiter=' ')
        SET_RES_RANGE = SCPIValueCommand('RES:RANG', delimiter=' ')
        
        SET_VOLT_DC_AUTO = SCPIValueCommand('VOLT:DC:RANG:AUTO', delimiter=' ')
        SET_VOLT_AC_AUTO = SCPIValueCommand('VOLT:AC:RANG:AUTO', delimiter=' ')
        SET_CURR_DC_AUTO = SCPIValueCommand('CURR:DC:RANG:AUTO', delimiter=' ')
        SET_CURR_AC_AUTO = SCPIValueCommand('CURR:AC:RANG:AUTO', delimiter=' ')
        SET_CAP_AUTO = SCPIValueCommand('CAP:RANG:AUTO', delimiter=' ')
        SET_RES_AUTO = SCPIValueCommand('RES:RANG:AUTO', delimiter=' ')


    class Ranges(Enum):
        """
        Available ranges to be used in setting specific modes of the device.
        Values correspond to the discrete range values.
        """
        # DC Voltage: 200mV, 2V, 20V, 200V, 1000V
        DC_200MV = '0.2'
        DC_2V = '2'
        DC_20V = '20'
        DC_200V = '200'
        DC_1000V = '1000'
        
        # AC Voltage: 200mV, 2V, 20V, 200V, 750V
        AC_200MV = '0.2'
        AC_2V = '2'
        AC_20V = '20'
        AC_200V = '200'
        AC_750V = '750'
        
        # DC Current: 200mA, 10A
        DC_200MA = '0.2'
        DC_10A = '10'
        
        # AC Current: 200mA, 10A
        AC_200MA = '0.2'
        AC_10A = '10'
        
        # Resistance: 200, 2k, 20k, 200k, 2M, 20M, 100M
        RES_200R = '200'
        RES_2KR = '2E3'
        RES_20KR = '20E3'
        RES_200KR = '200E3'
        RES_2MR = '2E6'
        RES_20MR = '20E6'
        RES_100MR = '100E6'
        
        # Capacitance: 2nF, 20nF, 200nF, 2uF, 20uF, 200uF, 10mF
        CAP_2NF = '2E-9'
        CAP_20NF = '20E-9'
        CAP_200NF = '200E-9'
        CAP_2UF = '2E-6'
        CAP_20UF = '20E-6'
        CAP_200UF = '200E-6'
        CAP_10MF = '10E-3'

        AUTO = 'AUTO'

        FREQ_HZ = 'FREQ_HZ'

    class Units(Enum):
        """
        Available units user can specify in measuring methods
        """
        UNIT_MV = '1e3'  # miliVolts
        UNIT_V = '1'  # Volts

        UNIT_UA = '1e-6'  # microAmps
        UNIT_MA = '1e-3'  # miliAmps
        UNIT_A = '1'  # Amps

        UNIT_NF = '1e-9'  # nanoFarads
        UNIT_UF = '1e-6'  # microFarads
        UNIT_MF = '1e-3'  # miliFarads
        UNIT_M = '1'  # Farads

        UNIT_R = '1'  # Ohms
        UNIT_KR = '1e3'  # kiloOhms
        UNIT_MR = '1e6'  # MegaOhms

        UNIT_HZ = '1'  # Hz

    class Modes(Enum):
        """
        Available measurement modes of the device
        """
        VOLT = 'VOLT:DC'
        CURR = 'CURR:DC'
        VOLT_AC = 'VOLT:AC'
        CURR_AC = 'CURR:AC'
        RES = 'RES'
        CAP = 'CAP'
        DIOD = 'DIOD'
        CONT = 'CONT'

    def __init__(self, params):
        Multimeters.__init__(self, params)
        SCPICommunicable.__init__(self, params['interface'])

        self.determine_suffix(self.Commands.GET_INFO)

        self.VOLTAGE_UNITS = [self.Units.UNIT_MV, self.Units.UNIT_V]
        self.CURRENT_UNITS = [self.Units.UNIT_UA, self.Units.UNIT_MA, self.Units.UNIT_A]
        self.RESISTANCE_UNITS = [self.Units.UNIT_R, self.Units.UNIT_KR, self.Units.UNIT_MR]
        self.CAPACITANCE_UNITS = [self.Units.UNIT_NF, self.Units.UNIT_UF, self.Units.UNIT_MF, self.Units.UNIT_M]

        # Collecting possible device modes from the Modes enum class
        self.possible_modes = [mode.name for mode in self.Modes]

        self.mode = None

    def _measure_value(self):
        response = self.transceive(self.Commands.MEASURE).strip('\r\n')
        try:
            parts = response.split()
            if len(parts) >= 2:
                return float(parts[1])
            return float(response)
        except (ValueError, IndexError):
            if 'OL' in response:
                self.logger.error(f"Device is overloaded: '{response}'. Please change the range.", extra=self.log_args)
                return None
            self.logger.error(f"Incorrect value received from the device: '{response}'", extra=self.log_args)
            return None

    def _detect_mode(self) -> Modes:
        """
        This method asks the device for the current mode setting using CONF? query.
        """
        # Try up to 3 times in case of slow response/timeout
        mode_received = ""
        for _ in range(3):
            mode_received = self.transceive(self.Commands.GET_MODE)
            if mode_received:
                break

        for mode in self.Modes:
            if mode.value in mode_received:
                self.mode = mode
                return self.mode
        
        raise ValueError(f"Mode received in an incorrect format. Received message: {mode_received}")

    def is_mode(self, mode) -> bool:
        if isinstance(mode, self.Modes):
            current_mode = self._detect_mode()
            if mode == current_mode:
                return True
            else:
                return False
        else:
            self.logger.error(f"Mode has to be of type MP71.Modes, not {type(mode)}", extra=self.log_args)
            return False

    def get_info(self):
        device_info = self.transceive(self.Commands.GET_INFO).replace(',', ', ').strip('\r\n')
        mode_val = self.transceive(self.Commands.GET_MODE).strip('\r\n')
        response = {"Device information": device_info, "Status": mode_val}
        return response

    def get_mode(self):
        mode = self.transceive(self.Commands.GET_MODE).strip('\r\n')
        return mode

    def get_range(self):
        """
        Queries the current range. 
        Note: Since ranges are mode-specific in this series, this returns the full CONF? string.
        """
        return self.transceive(self.Commands.GET_MODE).strip('\r\n')

    def detect_model(self):
        response = self.transceive(self.Commands.GET_INFO)

        if response and isinstance(response, str):
            split_response = response.split(',')
            if len(split_response) >= 3:
                series = split_response[0]
                model_str = split_response[1]
                serial_number = split_response[2]

                for model in self.Models:
                    if model_str in model.idn:
                        self._apply_model(model)
                        self.logger.info(f'Detected model {series} {model_str}', extra=self.log_args)
                        return

        raise LookupError('Unable to detect a valid Multicomp multimeter model.')

    def set_mode_voltage_dc(self, range=Ranges.DC_2V) -> None:
        """
        Sends a command to set the mode to voltage DC with specified range.

        :param range: Measuring range of the multimeter
        :type  range: MP71.Ranges
        """
        self.transceive(self.Commands.SET_MODE_VOLT_DC)
        if range == self.Ranges.AUTO:
            self.Commands.SET_VOLT_DC_AUTO.value = 'ON'
            self.transceive(self.Commands.SET_VOLT_DC_AUTO)
        else:
            self.Commands.SET_VOLT_DC_RANGE.value = range.value
            self.transceive(self.Commands.SET_VOLT_DC_RANGE)
            self.Commands.SET_VOLT_DC_AUTO.value = 'OFF'
            self.transceive(self.Commands.SET_VOLT_DC_AUTO)
        
        if self.is_mode(self.Modes.VOLT):
            self.mode = self.Modes.VOLT
            self.logger.info(f"Measurement mode has been set to Voltage DC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to VOLTAGE DC was not successful", extra=self.log_args)

    def set_mode_voltage_ac(self, range=Ranges.AC_2V) -> None:
        """
        Sends a command to set the mode to voltage AC with specified range.

        :param range: Measuring range of the multimeter
        :type  range: MP71.Ranges
        """
        self.transceive(self.Commands.SET_MODE_VOLT_AC)
        if range == self.Ranges.AUTO:
            self.Commands.SET_VOLT_AC_AUTO.value = 'ON'
            self.transceive(self.Commands.SET_VOLT_AC_AUTO)
        else:
            self.Commands.SET_VOLT_AC_RANGE.value = range.value
            self.transceive(self.Commands.SET_VOLT_AC_RANGE)
            self.Commands.SET_VOLT_AC_AUTO.value = 'OFF'
            self.transceive(self.Commands.SET_VOLT_AC_AUTO)
        
        if self.is_mode(self.Modes.VOLT_AC):
            self.mode = self.Modes.VOLT_AC
            self.logger.info(f"Measurement mode has been set to Voltage AC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to VOLTAGE AC was not successful", extra=self.log_args)

    def set_mode_current_dc(self, range=Ranges.DC_10A) -> None:
        """
        Sends a command to set the mode to current DC with specified range.

        :param range: Measuring range of the multimeter
        :type  range: MP71.Ranges
        """
        self.transceive(self.Commands.SET_MODE_CURR_DC)
        if range == self.Ranges.AUTO:
            self.Commands.SET_CURR_DC_AUTO.value = 'ON'
            self.transceive(self.Commands.SET_CURR_DC_AUTO)
        else:
            self.Commands.SET_CURR_DC_RANGE.value = range.value
            self.Commands.SET_CURR_DC_AUTO.value = 'OFF'
            self.transceive(self.Commands.SET_CURR_DC_RANGE)
            self.transceive(self.Commands.SET_CURR_DC_AUTO)
        
        if self.is_mode(self.Modes.CURR):
            self.mode = self.Modes.CURR
            self.logger.info(f"Measurement mode has been set to Current DC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to CURRENT DC was not successful", extra=self.log_args)

    def set_mode_current_ac(self, range=Ranges.AC_10A) -> None:
        """
        Sends a command to set the mode to current AC with specified range.

        :param range: Measuring range of the multimeter
        :type  range: MP71.Ranges
        """
        self.transceive(self.Commands.SET_MODE_CURR_AC)
        if range == self.Ranges.AUTO:
            self.Commands.SET_CURR_AC_AUTO.value = 'ON'
            self.transceive(self.Commands.SET_CURR_AC_AUTO)
        else:
            self.Commands.SET_CURR_AC_RANGE.value = range.value
            self.transceive(self.Commands.SET_CURR_AC_RANGE)
            self.Commands.SET_CURR_AC_AUTO.value = 'OFF'
            self.transceive(self.Commands.SET_CURR_AC_AUTO)
        
        if self.is_mode(self.Modes.CURR_AC):
            self.mode = self.Modes.CURR_AC
            self.logger.info(f"Measurement mode has been set to Current AC, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to CURRENT AC was not successful", extra=self.log_args)

    def set_mode_resistance(self, range=Ranges.RES_2MR):
        """
        Sends a command to set the mode to resistance with specified range.

        :param range: Measuring range of the multimeter
        :type  range: MP71.Ranges
        """
        self.transceive(self.Commands.SET_MODE_RES)
        if range == self.Ranges.AUTO:
            self.Commands.SET_RES_AUTO.value = 'ON'
            self.transceive(self.Commands.SET_RES_AUTO)
        else:
            self.Commands.SET_RES_RANGE.value = range.value
            self.transceive(self.Commands.SET_RES_RANGE)
            self.Commands.SET_RES_AUTO.value = 'OFF'
            self.transceive(self.Commands.SET_RES_AUTO)
        
        if self.is_mode(self.Modes.RES):
            self.mode = self.Modes.RES
            self.logger.info(f"Measurement mode has been set to Resistance, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to RESISTANCE was not successful", extra=self.log_args)

    def set_mode_capacitance(self, range=Ranges.CAP_2UF):
        """
        Sends a command to set the mode to capacitance with specified range.

        :param range: Measuring range of the multimeter
        :type  range: MP71.Ranges
        """
        self.transceive(self.Commands.SET_MODE_CAP)
        if range == self.Ranges.AUTO:
            self.Commands.SET_CAP_AUTO.value = 'ON'
            self.transceive(self.Commands.SET_CAP_AUTO)
        else:
            self.Commands.SET_CAP_RANGE.value = range.value
            self.transceive(self.Commands.SET_CAP_RANGE)
            self.Commands.SET_CAP_AUTO.value = 'OFF'
            self.transceive(self.Commands.SET_CAP_AUTO)
        
        if self.is_mode(self.Modes.CAP):
            self.mode = self.Modes.CAP
            self.logger.info(f"Measurement mode has been set to Capacitance, range: {range.name}", extra=self.log_args)
        else:
            self.logger.error(f"Setting the mode to CAPACITANCE was not successful", extra=self.log_args)

    def measure_capacitance(self, unit=Units.UNIT_MF) -> float:
        """
        Sends a query command to get a measurement of Capacitance.
        Returns measured capacitance in the specified unit.

        :param unit: The output unit
        :type  unit: MP71.Units
        """
        if self.mode != self.Modes.CAP:
            self.logger.error(
                msg=f"Device is not in the correct state - CAPACITANCE [Modes.CAP]. Current mode: {self.mode}",
                extra=self.log_args
            )
            return None

        if unit not in self.CAPACITANCE_UNITS:
            raise ValueError(f'Unit {unit} is not supported (part of CAPACITANCE_UNITS)')

        multiplier = float(unit.value)

        result = self._measure_value()
        if result is not None:
            result *= multiplier
        return result

    def measure_resistance(self, unit=Units.UNIT_R) -> float:
        """
        Sends a query command to get a measurement of Resistance.
        Returns measured resistance in the specified unit.

        :param unit: The output unit
        :type  unit: MP71.Units
        """
        if self.mode != self.Modes.RES:
            self.logger.error(
                msg=f"Device is not in the correct state - RESISTANCE [Modes.RES]. Current mode: {self.mode}",
                extra=self.log_args
            )
            return None

        if unit not in self.RESISTANCE_UNITS:
            raise ValueError(f'Unit {unit} is not supported (part of RESISTANCE_UNITS)')

        multiplier = float(unit.value)

        result = self._measure_value()
        if result is not None:
            result *= multiplier
        return result

    def measure_voltage(self, unit=Units.UNIT_V) -> float:
        """
        Sends a query command to get a measurement of Voltage.

        :param unit: The output unit
        :type  unit: MP71.Units
        """
        if unit not in self.VOLTAGE_UNITS:
            raise ValueError(f'Unit {unit} is not supported (part of VOLTAGE_UNITS)')
 
        multiplier = float(unit.value)

        result = self._measure_value()
        if result is not None:
            result *= multiplier
        return result

    def measure_current(self, unit=Units.UNIT_A) -> float:
        """
        Sends a query command to get a measurement of Current.
        Base function for both DC and AC current measurement
        Returns measured current in the specified unit.

        :param unit: The output unit
        :type  unit: MP71.Units
        """
        if unit not in self.CURRENT_UNITS:
            raise ValueError(f'Unit {unit} is not supported (part of CURRENT_UNITS)')
        
        multiplier = float(unit.value)

        result = self._measure_value()
        if result is not None:
            result *= multiplier
        return result

    def measure_voltage_dc(self, unit=Units.UNIT_V) -> float:
        """
        Checks the correct mode and calls the measure_voltage() method.
        Returns measured voltage in the specified unit.

        :param unit: The output unit
        :type  params: MP71.Units
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
        :type  params: MP71.Units
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
        :type  params: MP71.Units
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
        :type  params: MP71.Units
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

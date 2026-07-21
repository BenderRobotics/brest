# -*- coding: utf-8 -*-
"""
    brest.loads.tenma
    ~~~~~~~~~~~~~~~~~

    This module implements the Tenma Programmable DC Electronic Loads.

    :copyright: 2026 Bender Robotics
"""

from brest.communication import SCPICommunicable, SCPICommand, SCPIQueryCommand, SCPIValueCommand
from brest.loads import Loads
from brest.loads.models import SCPIModel
from brest.loads.configs import (
    TenmaDynamicCVConfig,
    TenmaDynamicCCConfig,
    TenmaDynamicCRConfig,
    TenmaDynamicCWConfig,
    TenmaOCPConfig
)

from enum import Enum
from typing import Union
from contextlib import suppress
from copy import deepcopy
from attrs import define, field, astuple

@define
class TenmaTelemetry:
    voltage: float
    current: float
    power: float

class Tenma(Loads, SCPICommunicable):
    """
    Tenma branded Programmable DC Electronic Load driver.

    Derived from: :class:`~brest.loads.Loads`, :class:`~brest.communication.SCPICommunicable`

    Implicit interface::

        interface:
            type: 'serial'
            timeout: 0.15
            vid: 0x0416
            pid: 0x5011

    This resource tries to disable itself upon destruction. To change this behavior, refert to
    :attr:`~brest.Resource.disable_on_destruct`.
    """

    Loads.KNOWN['Tenma'] = {
        'type': 'serial',
        'timeout': 0.15,
        'vid': 0x0416,
        'pid': 0x5011,
    }

    Models = [
        SCPIModel(
            'TENMA 72-13210', 1, 100, 120.0, 30.0, 300.0,
            [Loads.Protection.OVP, Loads.Protection.OCP, Loads.Protection.OPP, Loads.Protection.OTP],
            [Loads.Mode.CC, Loads.Mode.CV, Loads.Mode.CR, Loads.Mode.CW, Loads.Mode.DYNAMIC_CC, 
             Loads.Mode.DYNAMIC_CV, Loads.Mode.DYNAMIC_CR, Loads.Mode.DYNAMIC_CW,
             Loads.Mode.OCP]
        ),
    ]

    class Commands():
        GET_INFO = SCPIQueryCommand('*IDN')
        TRIGGER = SCPICommand('*TRG')

        EN_INPUT = SCPIValueCommand(":INP", delimiter=' ', value="ON")
        DIS_INPUT = SCPIValueCommand(":INP", delimiter=' ', value="OFF")
        GET_INPUT = SCPIQueryCommand(":INP")

        SET_MODE = SCPIValueCommand(":FUNC", delimiter=' ') 
        GET_MODE = SCPIQueryCommand(":FUNC")

        SET_CURRENT = SCPIValueCommand(":CURR", delimiter=' ')
        GET_CURRENT = SCPIQueryCommand(":CURR")
        SET_VOLTAGE = SCPIValueCommand(":VOLT", delimiter=' ')
        GET_VOLTAGE = SCPIQueryCommand(":VOLT")
        SET_RESISTANCE = SCPIValueCommand(":RES", delimiter=' ')
        GET_RESISTANCE = SCPIQueryCommand(":RES")
        SET_POWER = SCPIValueCommand(":POW", delimiter=' ')
        GET_POWER = SCPIQueryCommand(":POW")

        MEAS_VOLTAGE = SCPIQueryCommand(":MEAS:VOLT")
        MEAS_CURRENT = SCPIQueryCommand(":MEAS:CURR")
        MEAS_POWER = SCPIQueryCommand(":MEAS:POW")

        SET_DYNAMIC = SCPIValueCommand(":DYN", delimiter=' ')
        GET_DYNAMIC = SCPIQueryCommand(":DYN")

        SET_OCP = SCPIValueCommand(":OCP", delimiter=' ')
        RECALL_OCP = SCPIValueCommand(":RCL:OCP", delimiter=' ')

    def __init__(self, params):
        Loads.__init__(self, params)
        SCPICommunicable.__init__(self, params['interface'])
        self.message_suffix = '\n'
        self.determine_suffix(self.Commands.GET_INFO)

    def __del__(self):
        self.release()

    def enable(self):
        """
        Enables the input of the load.
        """
        self.transceive(self.Commands.EN_INPUT)

    def disable(self):
        """
        Disables the input of the load.
        """
        self.transceive(self.Commands.DIS_INPUT)

    def trigger(self):
        """
        Simulates an external hardware trigger execution pulse.
        """
        self.transceive(self.Commands.TRIGGER)

    def release(self):
        """
        Releases the resource.

        If :attr:`~brest.Resource.disable_on_destruct` is True, the resource is disabled before release.
        """
        if self.disable_on_destruct:
            with suppress(Exception):
                self.disable()
        SCPICommunicable.release(self)

    def detect_model(self):
        response = self.transceive(self.Commands.GET_INFO)
        for model in self.Models:
            if model.detect(response):
                self._apply_model(model)
                break
        if not self.IDN:
            raise LookupError('Unable to detect a valid Tenma Load model.')

    @property
    def is_enabled(self) -> bool:
        """
        Checks if the load input is enabled.
        
        :return: True if enabled, False otherwise
        :rtype: bool
        """
        resp = self.transceive(self.Commands.GET_INPUT).strip().upper()
        on = ("1", "ON")
        return resp in on

    @property
    def current(self) -> float:
        """
        Gets the current load value.
        
        :return: Current load value
        :rtype: float
        """
        return self._get_quantity(self.Commands.GET_CURRENT, Loads.Units.AMP.value)

    @current.setter
    def current(self, value: float):
        """
        Sets the current load value.
        
        :param value: Current load value
        :type  value: float
        """
        self._set_quantity(self.Commands.SET_CURRENT, value, self.MAX_CURRENT, Loads.Units.AMP.value)

    @property
    def voltage(self) -> float:
        """
        Gets the voltage load value.
        
        :return: Voltage load value
        :rtype: float
        """
        return self._get_quantity(self.Commands.GET_VOLTAGE, Loads.Units.VOLT.value)

    @voltage.setter
    def voltage(self, value: float):
        """
        Sets the voltage load value.
        
        :param value: Voltage load value
        :type  value: float
        """
        self._set_quantity(self.Commands.SET_VOLTAGE, value, self.MAX_VOLTAGE, Loads.Units.VOLT.value)

    @property
    def power(self) -> float:
        """
        Gets the power load value.
        
        :return: Power load value
        :rtype: float
        """
        return self._get_quantity(self.Commands.GET_POWER, Loads.Units.WATT.value)

    @power.setter
    def power(self, value: float):
        """
        Sets the power load value.
        
        :param value: Power load value
        :type  value: float
        """
        self._set_quantity(self.Commands.SET_POWER, value, self.MAX_POWER, Loads.Units.WATT.value)

    @property
    def resistance(self) -> float:
        """
        Gets the resistance load value.
        
        :return: Resistance load value
        :rtype: float
        """
        return self._get_quantity(self.Commands.GET_RESISTANCE, Loads.Units.OHM.value)

    @resistance.setter
    def resistance(self, value: float):
        """
        Sets the resistance load value.
        
        :param value: Resistance load value
        :type  value: float
        """
        self._set_quantity(self.Commands.SET_RESISTANCE, value, None, Loads.Units.OHM.value)

    def measure(self, quantity: Loads.Quantity = Loads.Quantity.ALL) -> Union[float, TenmaTelemetry]:
        """
        Measures any of the selected metrics or all at once.

        :param quantity: Desired measurement quantity
        :type  quantity: :class:`~brest.loads.Loads.Quantity`
        
        :return: Measured quantity or telemetry snapshot
        :rtype: float or :class:`~brest.loads.TenmaTelemetry`
        """
        if quantity == Loads.Quantity.VOLTAGE:
            raw = self.transceive(self.Commands.MEAS_VOLTAGE)
            return self._to_float_with_unit(raw, Loads.Units.VOLT.value)

        if quantity == Loads.Quantity.CURRENT:
            raw = self.transceive(self.Commands.MEAS_CURRENT)
            return self._to_float_with_unit(raw, Loads.Units.AMP.value)

        if quantity == Loads.Quantity.POWER:
            raw = self.transceive(self.Commands.MEAS_POWER)
            return self._to_float_with_unit(raw, Loads.Units.WATT.value)

        if quantity == Loads.Quantity.ALL:
            voltage_raw = self.transceive(self.Commands.MEAS_VOLTAGE)
            current_raw = self.transceive(self.Commands.MEAS_CURRENT)
            power_raw = self.transceive(self.Commands.MEAS_POWER)

            return TenmaTelemetry(
                voltage=self._to_float_with_unit(voltage_raw, Loads.Units.VOLT.value),
                current=self._to_float_with_unit(current_raw, Loads.Units.AMP.value),
                power=self._to_float_with_unit(power_raw, Loads.Units.WATT.value)
            )

        self.logger.warning(f"Unsupported measurement metric quantity: {quantity}", extra=self.log_args)

    @property
    def mode(self) -> Loads.Mode:
        """
        Gets current operating mode.

        :return: Current mode
        :rtype: :class:`~brest.loads.Loads.Mode`
        """
        resp = self.transceive(self.Commands.GET_MODE).strip().upper()
        try:
            return Loads.Mode(resp) 
        except ValueError:
            self.logger.error(f"Load returned unrecognized mode: '{resp}'", extra=self.log_args)

    @mode.setter
    def mode(self, target_mode: Loads.Mode) -> None:
        """
        Sets operating mode after validation.

        :param target_mode: Target mode to set
        :type  target_mode: :class:`~brest.loads.Loads.Mode`
        """
        if not isinstance(target_mode, Loads.Mode):
            self.logger.error(f"Invalid mode type: {target_mode}", extra=self.log_args)
            return

        if self.is_enabled:
            self.logger.error(f"Input must be disabled to change mode. Use disable().", extra=self.log_args)
            return

        if self.mode == target_mode:
            self.logger.info(f"Mode is already set to {target_mode}", extra=self.log_args)
            return

        cmd = deepcopy(self.Commands.SET_MODE)
        self.logger.debug(f"Setting mode to: {target_mode}", extra=self.log_args)
        cmd.value = target_mode.value
        self.transceive(cmd)

    def configure_dynamic_mode(self, config: Union[TenmaDynamicCVConfig, TenmaDynamicCCConfig, 
                                TenmaDynamicCRConfig, TenmaDynamicCWConfig]) -> None:
        """
        Configures dynamic mode with validation.

        :param config: Dynamic mode configuration
        :type  config: Union[TenmaDynamicCVConfig, TenmaDynamicCCConfig, TenmaDynamicCRConfig, TenmaDynamicCWConfig]
        """
        if not isinstance(config, (TenmaDynamicCVConfig, TenmaDynamicCCConfig, TenmaDynamicCRConfig, TenmaDynamicCWConfig)):
            self.logger.error(f"Invalid config type: {config}", extra=self.log_args)
            return

        if self.is_enabled:
            self.logger.error(f"Input must be disabled to change mode. Use disable().", extra=self.log_args)
            return

        if not isinstance(config.mode, Loads.Mode) or not config.mode.name.startswith("DYNAMIC_"):
            self.logger.error(f"Invalid mode type: {config.mode}", extra=self.log_args)
            return

        # Query whether we need to change the mode as well
        set_mode = self.mode
        if set_mode != config.mode:
            self.logger.info(f"Changing mode from {set_mode} to {config.mode}", extra=self.log_args)
            self.mode = config.mode

        if config.mode == Loads.Mode.DYNAMIC_CV:
            limit = self.MAX_VOLTAGE
        elif config.mode == Loads.Mode.DYNAMIC_CC:
            limit = self.MAX_CURRENT
        elif config.mode == Loads.Mode.DYNAMIC_CR:
            limit = self.MAX_RESISTANCE
        elif config.mode == Loads.Mode.DYNAMIC_CW:
            limit = self.MAX_POWER
        else:
            limit = None

        try:
            config.validate(limit)
        except ValueError as e:
            self.logger.error(f"Invalid config values: {e}", extra=self.log_args)
            return

        cmd = deepcopy(self.Commands.SET_DYNAMIC)
        cmd.value = config
        self.transceive(cmd)

        # Must be queried to enter dynamic mode
        cmd = deepcopy(self.Commands.GET_DYNAMIC)
        self.transceive(cmd)

    def configure_ocp_mode(self, memory_slot: int, config: TenmaOCPConfig, recall: bool = True) -> None:
        """
        Configures overcurrent protection mode for selected memory slot.
        Optionally recall the configuration to active memory slot to be used immediately.

        :param memory_slot: Memory slot to configure
        :type  memory_slot: int
        :param config: Overcurrent protection configuration
        :type  config: :class:`~brest.loads.configs.tenma.TenmaOCPConfig`
        :param recall: Whether to recall the config to the active memory slot
        :type  recall: bool = True
        """
        if memory_slot < 1 or memory_slot > self.MEMORIES:
            self.logger.error(f"Memory slot {memory_slot} out of range 1-{self.MEMORIES}", extra=self.log_args)
            return

        if not isinstance(config, TenmaOCPConfig):
            self.logger.error(f"Invalid config type: {config}", extra=self.log_args)
            return

        try: 
            config.validate()
        except ValueError as e:
            self.logger.error(f"Invalid config values: {e}", extra=self.log_args)
            return

        # Build command value from config
        cmd_value = f"{memory_slot},{config}"

        cmd = deepcopy(self.Commands.SET_OCP)
        cmd.value = cmd_value
        self.transceive(cmd)

        # Recall the config to the active memory slot
        if recall:
            self.recall_ocp_mode(memory_slot)

    def recall_ocp_mode(self, memory_slot: int) -> None:
        """
        Recalls overcurrent protection mode from memory slot to active mode.

        :param memory_slot: Memory slot to recall
        :type  memory_slot: int
        """
        if memory_slot < 1 or memory_slot > self.MEMORIES:
            self.logger.error(f"Memory slot {memory_slot} out of range 1-{self.MEMORIES}", extra=self.log_args)
            return
        
        cmd = deepcopy(self.Commands.RECALL_OCP)
        cmd.value = memory_slot
        self.transceive(cmd)

    def _set_quantity(self, cmd, value: float, max_limit: float, unit: str) -> None:
        """
        Universal setter that handles boundary validation, logging, and SCPI transmission.
        
        :param cmd: SCPI command to use
        :type  cmd: SCPICommand
        :param value: Value to set
        :type  value: float
        :param max_limit: Maximum allowed value
        :type  max_limit: float
        :param unit: Unit of measurement
        :type  unit: str
        """
        if not isinstance(value, (int, float)):
            msg = f"Invalid type {type(value).__name__} for setting quantity. Expected int or float."
            self.logger.error(msg, extra=self.log_args)
            return

        if max_limit is not None and value > max_limit:
            msg = f"Value {value}{unit} exceeds hardware limit {max_limit}{unit}."
            self.logger.error(msg, extra=self.log_args)
            return

        if value < 0.0:
            msg = f"Load value cannot be set to negative: {value}{unit}."
            self.logger.error(msg, extra=self.log_args)
            return

        cmd.value = f"{value}{unit}"
        self.transceive(cmd)

    def _get_quantity(self, cmd, unit: str) -> float:
        """
        Universal getter engine that strips hardware units and safely casts to float.
        
        :param cmd: SCPI command to use
        :type  cmd: SCPICommand
        :param unit: Unit of measurement
        :type  unit: str
        :return: Measured quantity as float
        :rtype: float
        """
        raw_resp = self.transceive(cmd)
        return self._to_float_with_unit(raw_resp, unit)
    
    def _to_float_with_unit(self, value, unit: str) -> float:
        """
        Response parser that strips hardware units and safely casts to float.

        :param value: Response to parse
        :type  value: str
        :param unit: Unit of measurement
        :type  unit: str
        :return: Measured quantity as float
        :rtype: float
        """
        try:
            return float(value.lstrip('>').strip().rstrip(unit))
        except (TypeError, ValueError):
            msg = f"Failed to parse response '{value}' for unit '{unit}'."
            self.logger.error(msg, extra=self.log_args)
            return None

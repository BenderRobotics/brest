# -*- coding: utf-8 -*-
"""
    brest.loads.configs.tenma
    ~~~~~~~~~~~~~~~~~

    This module implements the configurations data structures for the Tenma 72-13210 
    Programmable DC Electronic Load.

    :copyright: 2026 Bender Robotics
"""

from enum import Enum
from attrs import define, field, astuple, validators
from brest.loads import Loads

class ModeIndex(Enum):
    CV = 1
    CC = 2
    CR = 3
    CW = 4

@define
class TenmaDynamicCVConfig:
    """
    Configuration structure for constant voltage mode.

    :param voltage1: Voltage level 1
    :type  voltage1: float
    :param voltage2: Voltage level 2
    :type  voltage2: float
    :param frequency: Frequency of the voltage waveform
    :type  frequency: float
    :param duty_cycle: Duty cycle of the voltage waveform
    :type  duty_cycle: float
    :raises ValueError: If any of the parameters are out of range
    """
    voltage1: float = field(converter=float, validator=[validators.ge(0.0)])
    voltage2: float = field(converter=float, validator=[validators.ge(0.0)])
    frequency: float = field(converter=float, validator=[validators.ge(0.0)])
    duty_cycle: float = field(converter=float, validator=[validators.lt(100.0)])
    mode: Loads.Mode = Loads.Mode.DYNAMIC_CV

    def __str__(self):
        return (
            f"{ModeIndex.CV.value},"
            f"{self.voltage1:.4f}V,"
            f"{self.voltage2:.4f}V,"
            f"{self.frequency:.4f}HZ,"
            f"{self.duty_cycle:.4f}%"
        )

    def validate(self, limit: float):
        if self.voltage2 > limit or self.voltage1 > limit:
            raise ValueError("Voltage value out of set limits")


@define
class TenmaDynamicCCConfig:
    """
    Configuration structure for constant current mode.

    :param slope1: Slope level 1
    :type  slope1: float
    :param slope2: Slope level 2
    :type  slope2: float
    :param current1: Current level 1
    :type  current1: float
    :param current2: Current level 2
    :type  current2: float
    :param frequency: Frequency of the current waveform
    :type  frequency: float
    :param duty_cycle: Duty cycle of the current waveform
    :type  duty_cycle: float
    :raises ValueError: If any of the parameters are out of range
    """
    slope1: float = field(converter=float, validator=[validators.ge(0.0)])
    slope2: float = field(converter=float, validator=[validators.ge(0.0)])
    current1: float = field(converter=float, validator=[validators.ge(0.0)])
    current2: float = field(converter=float, validator=[validators.ge(0.0)])
    frequency: float = field(converter=float, validator=[validators.ge(0.0)])
    duty_cycle: float = field(converter=float, validator=[validators.lt(100.0)])
    mode: Loads.Mode = Loads.Mode.DYNAMIC_CC

    def __str__(self) -> str:
        return (
            f"{ModeIndex.CC.value},"
            f"{self.slope1:.4f}A/uS,"
            f"{self.slope2:.4f}A/uS,"
            f"{self.current1:.4f}A,"
            f"{self.current2:.4f}A,"
            f"{self.frequency:.4f}HZ,"
            f"{self.duty_cycle:.4f}%"
        )

    def validate(self, limit: float):
        if self.current2 > limit or self.current1 > limit:
            raise ValueError("Current values must be below current range")


@define
class TenmaDynamicCRConfig:
    """
    Configuration structure for constant resistance mode.

    :param resistance1: Resistance level 1
    :type  resistance1: float
    :param resistance2: Resistance level 2
    :type  resistance2: float
    :param frequency: Frequency of the resistance waveform
    :type  frequency: float
    :param duty_cycle: Duty cycle of the resistance waveform
    :type  duty_cycle: float
    :raises ValueError: If any of the parameters are out of range
    """
    resistance1: float = field(converter=float, validator=[validators.ge(0.0)])
    resistance2: float = field(converter=float, validator=[validators.ge(0.0)])
    frequency: float = field(converter=float, validator=[validators.ge(0.0)])
    duty_cycle: float = field(converter=float, validator=[validators.lt(100.0)])
    mode: Loads.Mode = Loads.Mode.DYNAMIC_CR

    def __str__(self) -> str:
        return (
            f"{ModeIndex.CR.value},"
            f"{self.resistance1:.4f}OHM,"
            f"{self.resistance2:.4f}OHM,"
            f"{self.frequency:.4f}HZ,"
            f"{self.duty_cycle:.4f}%"
        )

    def validate(self, limit: float):
        if self.resistance2 > limit or self.resistance1 > limit:
            raise ValueError("Resistance value out of set limits")


@define
class TenmaDynamicCWConfig:
    """
    Configuration structure for constant power mode.

    :param power1: Power level 1
    :type  power1: float
    :param power2: Power level 2
    :type  power2: float
    :param frequency: Frequency of the power waveform
    :type  frequency: float
    :param duty_cycle: Duty cycle of the power waveform
    :type  duty_cycle: float
    :raises ValueError: If any of the parameters are out of range
    """
    power1: float = field(converter=float, validator=[validators.ge(0.0)])
    power2: float = field(converter=float, validator=[validators.ge(0.0)])
    frequency: float = field(converter=float, validator=[validators.ge(0.0)])
    duty_cycle: float = field(converter=float, validator=[validators.lt(100.0)])
    mode: Loads.Mode = Loads.Mode.DYNAMIC_CW

    def __str__(self) -> str:
        return (
            f"{ModeIndex.CW.value},"
            f"{self.power1:.4f}W,"
            f"{self.power2:.4f}W,"
            f"{self.frequency:.4f}HZ,"
            f"{self.duty_cycle:.4f}%"
        )

    def validate(self, limit: float):
        if self.power2 > limit or self.power1 > limit:
            raise ValueError("Power value out of set limits")

@define
class TenmaOCPConfig:
    """
    Configuration structure for overcurrent protection mode.

    :param von_volt: Voltage when OCP is enabled
    :type  von_volt: float
    :param von_delay: Delay before OCP is enabled
    :type  von_delay: float
    :param current_range: Current range
    :type  current_range: float
    :param start_current: Starting current
    :type  start_current: float
    :param step_current: Current step
    :type  step_current: float
    :param step_delay: Delay between current steps
    :type  step_delay: float
    :param cutoff_current: Cutoff current
    :type  cutoff_current: float
    :param ocp_volt: Voltage at which OCP is triggered
    :type  ocp_volt: float
    :param max_overcurrent: Maximum overcurrent
    :type  max_overcurrent: float
    :param min_overcurrent: Minimum overcurrent
    :type  min_overcurrent: float
    :raises ValueError: If any of the parameters are out of range
    """
    von_volt: float = field(converter=float)
    von_delay: float = field(converter=float)
    current_range: float = field(converter=float)
    start_current: float = field(converter=float)
    step_current: float = field(converter=float)
    step_delay: float = field(converter=float)
    cutoff_current: float = field(converter=float)
    ocp_volt: float = field(converter=float)
    max_overcurrent: float = field(converter=float)
    min_overcurrent: float = field(converter=float)

    def __str__(self):
        return (
            f"{self.von_volt:.4f}V,"
            f"{self.von_delay:.4f}S,"
            f"{self.current_range:.4f}A,"
            f"{self.start_current:.4f}A,"
            f"{self.step_current:.4f}A,"
            f"{self.step_delay:.4f}S,"
            f"{self.cutoff_current:.4f}A,"
            f"{self.ocp_volt:.4f}V,"
            f"{self.max_overcurrent:.4f}A,"
            f"{self.min_overcurrent:.4f}A"
        )

    def validate(self):
        if self.start_current > self.current_range:
            raise ValueError("Start current must be below current range")
        if self.start_current <= self.max_overcurrent:
            raise ValueError("Start current must be above max overcurrent")
        if self.cutoff_current > self.min_overcurrent:
            raise ValueError("Cut-off current must be below other current values")
        if self.max_overcurrent <= self.min_overcurrent:
            raise ValueError("Max overcurrent must be above min overcurrent")
        if self.step_current > self.start_current:
            raise ValueError("Current step must be same or lower than initial current")

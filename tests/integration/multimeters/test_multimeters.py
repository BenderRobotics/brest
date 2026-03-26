from dataclasses import dataclass, fields
import pytest
from unittest.mock import patch, call
import brest
from brest.communication import SCPICommunicable, SerialCommunicable
from brest.multimeters.multicomp import Multicomp
from brest.multimeters.mp71 import MP71

# import debugpy
# debugpy.listen(("localhost", 5678))
# print("Waiting for debugger...")
# debugpy.wait_for_client()

@dataclass
class FakeCom:
    vid: str
    pid: str
    serial: str
    port: str

@dataclass
class MultiCommand:
    cmds: list
    responses: list = None

@dataclass
class MultiCommandsList:
    measure_voltage_dc: callable = None
    measure_voltage_ac: callable = None
    measure_current_dc: callable = None
    measure_current_ac: callable = None
    measure_resistance: callable = None
    measure_capacitance: callable = None
    set_mode_voltage_dc: callable = None
    set_mode_voltage_ac: callable = None
    set_mode_current_dc: callable = None
    set_mode_current_ac: callable = None
    set_mode_resistance: callable = None
    set_mode_capacitance: callable = None
    set_mode_temperature: callable = None
    set_mode_frequency: callable = None
    measure_temperature: callable = None
    measure_frequency: callable = None

MULTI_COMMANDS = {
    "multimeters.Multicomp": MultiCommandsList(
        measure_voltage_dc=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"]),
        measure_voltage_ac=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"]),
        measure_current_dc=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"]),
        measure_current_ac=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"]),
        measure_resistance=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"]),
        measure_capacitance=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"]),
        set_mode_voltage_dc=lambda: MultiCommand(cmds=[b"CONF:VOLT:DC 5", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"1.0", b"VOLT"]),
        set_mode_voltage_ac=lambda: MultiCommand(cmds=[b"CONF:VOLT:AC 5", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"1.0", b"VOLT:AC"]),
        set_mode_current_dc=lambda: MultiCommand(cmds=[b"CONF:CURR:DC 10", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"1.0", b"CURR"]),
        set_mode_current_ac=lambda: MultiCommand(cmds=[b"CONF:CURR:AC 10", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"1.0", b"CURR:AC"]),
        set_mode_resistance=lambda: MultiCommand(cmds=[b"CONF:RES 50E6", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"1.0", b"RES"]),
        set_mode_capacitance=lambda: MultiCommand(cmds=[b"CONF:CAP 50E-3", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"1.0", b"CAP"]),
        set_mode_temperature=lambda: MultiCommand(cmds=[b"CONF:TEMP:RTD KITS90", b"TEMP:RTD:UNIT C", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"OK", b"1.0", b"TEMP"]),
        set_mode_frequency=lambda: MultiCommand(cmds=[b"CONF:FREQ", b"RATE F", b"MEAS?", b"FUNC?"], responses=[b"OK", b"OK", b"1.0", b"FREQ"]),
        measure_temperature=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"]),
        measure_frequency=lambda: MultiCommand(cmds=[b"MEAS?"], responses=[b"1.0"])
    ),
    "multimeters.MP71": MultiCommandsList(
        measure_voltage_dc=lambda: MultiCommand(cmds=[b"CONF?"], responses=[b"1.0"]),
        measure_voltage_ac=lambda: MultiCommand(cmds=[b"CONF?"], responses=[b"1.0"]),
        measure_current_dc=lambda: MultiCommand(cmds=[b"CONF?"], responses=[b"1.0"]),
        measure_current_ac=lambda: MultiCommand(cmds=[b"CONF?"], responses=[b"1.0"]),
        measure_resistance=lambda: MultiCommand(cmds=[b"CONF?"], responses=[b"1.0"]),
        measure_capacitance=lambda: MultiCommand(cmds=[b"CONF?"], responses=[b"1.0"]),
        set_mode_voltage_dc=lambda: MultiCommand(cmds=[b"FUNC:VOLT:DC", b"VOLT:DC:RANG 2", b"VOLT:DC:RANG:AUTO OFF", b"CONF:ALL?"], responses=[b"1.0", b"1.0", b"1.0", b"VOLT:DC"]),
        set_mode_voltage_ac=lambda: MultiCommand(cmds=[b"FUNC:VOLT:AC", b"VOLT:AC:RANG 2", b"VOLT:AC:RANG:AUTO OFF", b"CONF:ALL?"], responses=[b"1.0", b"1.0", b"1.0", b"VOLT:AC"]),
        set_mode_current_dc=lambda: MultiCommand(cmds=[b"FUNC:CURR:DC", b"CURR:DC:RANG 10", b"CURR:DC:RANG:AUTO OFF", b"CONF:ALL?"], responses=[b"1.0", b"1.0", b"1.0", b"CURR:DC"]),
        set_mode_current_ac=lambda: MultiCommand(cmds=[b"FUNC:CURR:AC", b"CURR:AC:RANG 10", b"CURR:AC:RANG:AUTO OFF", b"CONF:ALL?"], responses=[b"1.0", b"1.0", b"1.0", b"CURR:AC"]),
        set_mode_resistance=lambda: MultiCommand(cmds=[b"FUNC:RES", b"RES:RANG 2E6", b"RES:RANG:AUTO OFF", b"CONF:ALL?"], responses=[b"1.0", b"1.0", b"1.0", b"RES"]),
        set_mode_capacitance=lambda: MultiCommand(cmds=[b"FUNC:CAP", b"CAP:RANG 2E-6", b"CAP:RANG:AUTO OFF", b"CONF:ALL?"], responses=[b"1.0", b"1.0", b"1.0", b"CAP"]),
        set_mode_temperature=lambda: MultiCommand(cmds=[], responses=[]),
        set_mode_frequency=lambda: MultiCommand(cmds=[], responses=[]),
        measure_temperature=lambda: MultiCommand(cmds=[], responses=[]),
        measure_frequency=lambda: MultiCommand(cmds=[], responses=[])
    )
}

@dataclass
class Scenario:
    class_name: str
    idn: bytes
    serial: FakeCom
    commands: MultiCommandsList

SCENARIOS = {
    "multicomp": Scenario(
        class_name="multimeters.Multicomp",
        idn=b"Multicomp,Pro,MP730889",
        serial=FakeCom(port="COM998", vid=0x1A86, pid=0x7523, serial="SN998"),
        commands=MULTI_COMMANDS["multimeters.Multicomp"]
    ),
    "mp71": Scenario(
        class_name="multimeters.MP71",
        idn=b"Multicomp,Pro,MP711132",
        serial=FakeCom(port="COM999", vid=0x1A86, pid=0x7523, serial="SN999"),
        commands=MULTI_COMMANDS["multimeters.MP71"]
    )
}

@pytest.fixture(params=SCENARIOS.keys())
def multi_env(request):
    """
    Mocks the serial communication environment for multimeters.
    """
    scenario = SCENARIOS[request.param]
    scenario_serial = scenario.serial

    config_data = {
        'test': {
            'multi_under_test': {
                'class_name': scenario.class_name,
            }
        }
    }

    with patch('serial.Serial') as mock_serial_class, \
        patch('brest.pyserial_tools.list_ports.comports') as mock_comports, \
        patch.object(SerialCommunicable, 'get_connections') as mock_conn, \
        patch.object(SerialCommunicable, 'probe') as mock_probe, \
        patch.object(SCPICommunicable, 'write_raw') as mock_write, \
        patch.object(SCPICommunicable, 'read_raw') as mock_read:
        
        mock_conn.return_value = [scenario_serial]
        mock_comports.return_value = [scenario_serial]
        
        mock_probe.return_value = [{
            'type': 'serial', 
            'port': scenario_serial.port,
            'vid': scenario_serial.vid,
            'pid': scenario_serial.pid
        }]

        mock_serial_instance = mock_serial_class.return_value
        mock_serial_instance.port = scenario_serial.port
        mock_serial_instance.isOpen.return_value = False

        # For proper instantiation of multimeters
        # Instantiation calls get_info which returns *IDN?
        mock_read.side_effect = [scenario.idn] * 10
        res = brest.Resources(projects='test', project_config=config_data)
        
        mock_read.side_effect = None
        mock_read.return_value = b"1.0" # Default response

        yield {
            "res": res,
            "mock_read": mock_read,
            "mock_write": mock_write,
            "scenario": scenario
        }

@dataclass
class CommandTest:
    test_name: str
    test_args: tuple
    action: callable
    expected_value: object
    validate_result: callable = None
    skip_condition: callable = None
    setup_action_name: str = None

TEST_CASES_COMMANDS = [
    # Measurements
    CommandTest("measure_voltage_dc", (), lambda m: m.measure_voltage_dc(), None,
                setup_action_name="set_mode_voltage_dc"),
    CommandTest("measure_voltage_ac", (), lambda m: m.measure_voltage_ac(), None,
                setup_action_name="set_mode_voltage_ac"),
    CommandTest("measure_current_dc", (), lambda m: m.measure_current_dc(), None,
                setup_action_name="set_mode_current_dc"),
    CommandTest("measure_current_ac", (), lambda m: m.measure_current_ac(), None,
                setup_action_name="set_mode_current_ac"),
    CommandTest("measure_resistance", (), lambda m: m.measure_resistance(), None,
                setup_action_name="set_mode_resistance"),
    CommandTest("measure_capacitance", (), lambda m: m.measure_capacitance(m.Units.UNIT_MF), None,
                setup_action_name="set_mode_capacitance"),
    
    # Modes setting (We need specific return values for some mode checks)
    CommandTest("set_mode_voltage_dc", (), lambda m: m.set_mode_voltage_dc(), None),
    CommandTest("set_mode_voltage_ac", (), lambda m: m.set_mode_voltage_ac(), None),
    CommandTest("set_mode_current_dc", (), lambda m: m.set_mode_current_dc(), None),
    CommandTest("set_mode_current_ac", (), lambda m: m.set_mode_current_ac(), None),
    CommandTest("set_mode_resistance", (), lambda m: m.set_mode_resistance(), None),
    CommandTest("set_mode_capacitance", (), lambda m: m.set_mode_capacitance(), None),
    
    # Multicomp specific
    CommandTest("set_mode_temperature", (), lambda m: m.set_mode_temperature(), None,
                skip_condition=lambda m: not hasattr(m, 'set_mode_temperature')),
    CommandTest("set_mode_frequency", (), lambda m: m.set_mode_frequency(), None,
                skip_condition=lambda m: not hasattr(m, 'set_mode_frequency')),
    CommandTest("measure_temperature", (), lambda m: m.measure_temperature(), 1.0,
                setup_action_name="set_mode_temperature",
                skip_condition=lambda m: not hasattr(m, 'measure_temperature')),
    CommandTest("measure_frequency", (), lambda m: m.measure_frequency(), 1.0,
                setup_action_name="set_mode_frequency",
                skip_condition=lambda m: not hasattr(m, 'measure_frequency')),
]

@pytest.mark.parametrize("test_case", TEST_CASES_COMMANDS, ids=lambda x: x.test_name)
def test_commands(multi_env, test_case):
    """Parametrized test for Multimeter commands."""
    multi = multi_env["res"]["multi_under_test"]
    
    if test_case.skip_condition and test_case.skip_condition(multi):
        pytest.skip(f"{test_case.test_name} not supported by this multimeter")
    
    cmd_func = getattr(multi_env["scenario"].commands, test_case.test_name, None)
    if not cmd_func:
        pytest.skip(f"{test_case.test_name} command not configured for this multimeter")
        
    multi_cmd = cmd_func(*test_case.test_args)
    if not multi_cmd.cmds: # for functions like set_mode_temperature on mp71
        pytest.skip(f"{test_case.test_name} not supported by this multimeter")

    if test_case.setup_action_name:
        setup_cmd_func = getattr(multi_env["scenario"].commands, test_case.setup_action_name, None)
        setup_cmd = setup_cmd_func() if setup_cmd_func else None
        
        if setup_cmd and setup_cmd.responses:
            multi_env["mock_read"].side_effect = setup_cmd.responses
        else:
            multi_env["mock_read"].return_value = b"1.0"

        setup_action = getattr(multi, test_case.setup_action_name)
        setup_action()    
        
    multi_env["mock_read"].side_effect = multi_cmd.responses if multi_cmd.responses else None
    if not multi_cmd.responses:
        multi_env["mock_read"].return_value = b"1.0"

    multi_env["mock_write"].call_args_list.clear()

    result = test_case.action(multi, *test_case.test_args)
    
    # Validation: assert that write was called with exact commands
    actual_cmds = [call[0][0] for call in multi_env["mock_write"].call_args_list]
    assert actual_cmds == multi_cmd.cmds, f"Expected commands {multi_cmd.cmds}, got {actual_cmds}"

    if test_case.expected_value is not None:
        assert result == test_case.expected_value, f"Expected {test_case.expected_value}, got {result}"
        
    if test_case.validate_result:
        assert test_case.validate_result(result), f"Validation failed for {result}"

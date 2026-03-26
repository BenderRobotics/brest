from dataclasses import dataclass, fields
import pytest
from unittest.mock import patch
import brest
from brest.communication import SCPICommunicable, SerialCommunicable

@dataclass
class FakeCom:
  vid: str
  pid: str
  serial: str
  port: str

@dataclass
class PSUCommand:
    cmd: str
    response: bytes = b"1.0"

@dataclass
class PSUCommandsList:
    set_voltage: callable = None
    set_current: callable = None
    enable: callable = None
    disable: callable = None
    ovp_on: callable = None
    ovp_off: callable = None
    ocp_on: callable = None
    ocp_off: callable = None
    save_memory: callable = None
    recall_memory: callable = None
    status: callable = None
    get_info: callable = None
    get_voltage: callable = None
    get_current: callable = None
    set_voltage_limit: callable = None
    set_current_limit: callable = None
    get_voltage_limit: callable = None
    get_current_limit: callable = None

@dataclass
class Scenario:
    class_name: str
    idn: bytes
    commands: PSUCommandsList
    serial: FakeCom
    init_responses: list
    voltage_range: list
    default_v: float

PSU_COMMANDS = {
    "supplies.Tenma": PSUCommandsList(
        set_voltage=lambda x: PSUCommand(cmd=f"VSET1:{x}".encode()),
        set_current=lambda x: PSUCommand(cmd=f"ISET1:{x}".encode()),
        get_voltage=lambda x: PSUCommand(cmd=b"VOUT1?", response=str(x).encode()),
        get_current=lambda x: PSUCommand(cmd=b"IOUT1?", response=str(x).encode()),
        enable=lambda: PSUCommand(cmd=b"OUT1"),
        disable=lambda: PSUCommand(cmd=b"OUT0"),
        ovp_on=lambda: PSUCommand(cmd=b"OVP1"),
        ovp_off=lambda: PSUCommand(cmd=b"OVP0"),
        ocp_on=lambda: PSUCommand(cmd=b"OCP1"),
        ocp_off=lambda: PSUCommand(cmd=b"OCP0"),
        save_memory=lambda x: PSUCommand(cmd=f"SAV{x}".encode()),
        recall_memory=lambda x: PSUCommand(cmd=f"RCL{x}".encode()),
        status=lambda x: PSUCommand(cmd=b"STATUS?", response=x),
        get_info=lambda x: PSUCommand(cmd=b"*IDN?", response=x)
    ),
    "supplies.MP71": PSUCommandsList(
        set_voltage=lambda x: PSUCommand(cmd=f"VOLT {x}".encode(), response=b"5.0"),
        set_current=lambda x: PSUCommand(cmd=f"CURR {x}".encode(), response=b"0.1"),
        get_voltage=lambda x: PSUCommand(cmd=b"MEAS:VOLT?", response=str(x).encode()),
        get_current=lambda x: PSUCommand(cmd=b"MEAS:CURR?", response=str(x).encode()),
        enable=lambda: PSUCommand(cmd=b"OUTP 1"),
        disable=lambda: PSUCommand(cmd=b"OUTP 0"),
        set_voltage_limit=lambda x: PSUCommand(cmd=f"VOLT:LIM {x}".encode(), response=b"10.0"),
        set_current_limit=lambda x: PSUCommand(cmd=f"CURR:LIM {x}".encode(), response=b"1.0"),
        get_voltage_limit=lambda x: PSUCommand(cmd=b"VOLT:LIM?", response=str(x).encode()),
        get_current_limit=lambda x: PSUCommand(cmd=b"CURR:LIM?", response=str(x).encode()),
        get_info=lambda x: PSUCommand(cmd=b"*IDN?", response=x)
    )
}

SCENARIOS = {
    "tenma": Scenario(
        class_name="supplies.Tenma",
        idn=b"TENMA 72-2535",
        commands=PSU_COMMANDS["supplies.Tenma"],
        serial=FakeCom(port="COM999", vid=0x0416, pid=0x5011, serial="SN999"),
        init_responses=[b"TENMA 72-2535"] * 3 + [b"1.0"] * 10,
        voltage_range=[0, 30],
        default_v=5.0
    ),
    "mp72": Scenario(
        class_name="supplies.MP72",
        idn=b"Multicomp Pro 72-2535",
        commands=PSU_COMMANDS["supplies.Tenma"],
        serial=FakeCom(port="COM999", vid=0x0416, pid=0x5011, serial="SN999"),
        init_responses=[b"Multicomp Pro 72-2535"] * 3 + [b"1.0"] * 10,
        voltage_range=[0, 30],
        default_v=5.0
    ),
    "mp71": Scenario(
        class_name="supplies.MP71",
        idn=b"Multicomp Pro MP711132",
        commands=PSU_COMMANDS["supplies.MP71"],
        serial=FakeCom(port="COM999", vid=0x1A86, pid=0x7523, serial="SN999"),
        init_responses=[b"Multicomp Pro MP711132"] * 2 + [b"1.0"] * 10,
        voltage_range=[0, 30],
        default_v=5.0
    )
}

@pytest.fixture(params=SCENARIOS.keys())
def psu_env(request):
    """
    Mocks the serial communication environment.
    """
    scenario = SCENARIOS[request.param]
    scenario_serial = scenario.serial

    config_data = {
        'test': {
            'psu_under_test': {
                'class_name': scenario.class_name,
                'default': {'voltage': scenario.default_v, 'current': 0.1},
                'required': {'voltage_range': scenario.voltage_range}
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

        # For proper instatiation of all supplies
        mock_read.side_effect = scenario.init_responses
        res = brest.Resources(projects='test', project_config=config_data)
        
        mock_read.side_effect = None
        mock_read.return_value = b"1.0" # Default response must be a float convertible value

        yield {
            "res": res,
            "mock_read": mock_read,
            "mock_write": mock_write,
            "scenario": scenario
        }

        for psu in res:
            psu.disable_on_destruct = False
            psu.release()

# Parametrize command tests with actions as callables
@dataclass
class CommandTest:
    test_name: str # represents the command
    test_args: tuple
    action: callable
    expected_value: object # If set, assert the result matches this value
    validate_result: callable = None
    skip_condition: callable = None

TEST_CASES_COMMANDS = [
    CommandTest("set_voltage", (5.0,), lambda psu, v: setattr(psu, 'voltage', v), None),
    CommandTest("set_current", (0.1,), lambda psu, c: setattr(psu, 'current', c), None),
    CommandTest("enable", (), lambda psu: psu.enable(), None),
    CommandTest("disable", (), lambda psu: psu.disable(), None),
    CommandTest("get_voltage", (5.0,), lambda psu, v: psu.voltage, 5.0),
    CommandTest("get_current", (0.1,), lambda psu, c: psu.current, 0.1),
    CommandTest("set_voltage_limit", (10.0,), lambda psu, v: setattr(psu, 'voltage_limit', v), None,
                skip_condition=lambda psu: not hasattr(psu, 'voltage_limit')),
    CommandTest("set_current_limit", (1,), lambda psu, c: setattr(psu, 'current_limit', c), None,
                skip_condition=lambda psu: not hasattr(psu, 'current_limit')),
    CommandTest("get_voltage_limit", (10.0,), lambda psu, v: psu.voltage_limit, 10.0,
                skip_condition=lambda psu: not hasattr(psu, 'voltage_limit')),
    CommandTest("get_current_limit", (1,), lambda psu, c: psu.current_limit, 1.0,
                skip_condition=lambda psu: not hasattr(psu, 'current_limit')),
    CommandTest("ovp_on", (), lambda psu: psu.enable_protection(psu.Protection.OVP), None,
                skip_condition=lambda psu: psu.Protection.OVP not in psu.PROTECTION),
    CommandTest("ovp_off", (), lambda psu: psu.disable_protection(psu.Protection.OVP), None,
                skip_condition=lambda psu: psu.Protection.OVP not in psu.PROTECTION),
    CommandTest("ocp_on", (), lambda psu: psu.enable_protection(psu.Protection.OCP), None,
                skip_condition=lambda psu: psu.Protection.OCP not in psu.PROTECTION),
    CommandTest("ocp_off", (), lambda psu: psu.disable_protection(psu.Protection.OCP), None,
                skip_condition=lambda psu: psu.Protection.OCP not in psu.PROTECTION),
    CommandTest("save_memory", (1,), lambda psu, mem: psu.save_memory(mem), None,
                skip_condition=lambda psu: not psu.MEMORIES),
    CommandTest("recall_memory", (1,), lambda psu, mem: psu.recall_memory(mem), None,
                skip_condition=lambda psu: not psu.MEMORIES),
    CommandTest("status", (bytes([0b00000001]),), lambda psu, status: psu.get_status(), None,
                validate_result=lambda result: getattr(result, "cvcc", None) and not getattr(result, "protection", None))
]

@pytest.mark.parametrize("test_case", TEST_CASES_COMMANDS, ids=lambda x: x.test_name)
def test_commands(psu_env, test_case):
    """Parametrized test for PSU commands (read/write/protect/memory/status)."""
    psu = psu_env["res"]["psu_under_test"]
    
    # Skip if command is not supported by this PSU
    cmd_func = getattr(psu_env["scenario"].commands, test_case.test_name, None)
    
    if not cmd_func or (test_case.skip_condition and test_case.skip_condition(psu)):
        pytest.skip(f"{test_case.test_name} not supported by this PSU")

    psu_cmd = cmd_func(*test_case.test_args)

    psu_env["mock_read"].return_value = psu_cmd.response

    result = test_case.action(psu, *test_case.test_args)
    
    psu_env["mock_write"].assert_called_with(psu_cmd.cmd)

    if test_case.expected_value:
        assert result == test_case.expected_value, f"Expected {test_case.expected_value}, got {result}"
        
    if test_case.validate_result:
        assert test_case.validate_result(result), f"Validation failed for {result}"


def test_power_cycle(psu_env):
    psu = psu_env["res"]["psu_under_test"]
    psu_env["mock_write"].call_args_list.clear()
    
    with patch('time.sleep'):
        psu.cycle(delay=0.1, timeout=0.1)
    
    # cycle() calls disable(), sleep, enable(), sleep.
    calls = psu_env["mock_write"].call_args_list
    cmds = [call[0][0] for call in calls]
    
    assert len(cmds) == 2

    cmds_expected = psu_env["scenario"].commands
    assert cmds[-2] == cmds_expected.disable().cmd
    assert cmds[-1] == cmds_expected.enable().cmd

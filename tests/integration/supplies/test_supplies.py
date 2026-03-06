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
    response: bytes = b"OK"

@dataclass
class PSUCommandsList:
    set_voltage: callable
    set_current: callable
    enable: callable
    disable: callable
    ovp_on: callable
    ovp_off: callable
    ocp_on: callable
    ocp_off: callable
    save_memory: callable
    recall_memory: callable
    status: callable
    get_info: callable
    get_voltage: callable
    get_current: callable

@dataclass
class Scenario:
    class_name: str
    idn: bytes
    commands: PSUCommandsList
    serial: FakeCom
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
    )
}

SCENARIOS = {
    "tenma_basic": Scenario(
        class_name="supplies.Tenma",
        idn=b"TENMA 72-2535",
        commands=PSU_COMMANDS["supplies.Tenma"],
        serial=FakeCom(port="COM999", vid=0x0416, pid=0x5011, serial="SN999"),
        voltage_range=[0, 30],
        default_v=5.0          
    ),
    "multicomp_tenmatype": Scenario(
        class_name="supplies.Tenma",
        idn=b"Multicomp Pro 72-2535",
        commands=PSU_COMMANDS["supplies.Tenma"],
        serial=FakeCom(port="COM999", vid=0x0416, pid=0x5011, serial="SN999"),
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

        # Initially set it to IDN response for correct model detection
        mock_read.return_value = scenario.idn

        yield {
            "res": brest.Resources(projects='test', project_config=config_data),
            "mock_read": mock_read,
            "mock_write": mock_write,
            "scenario": scenario
        }


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
    
    if test_case.skip_condition and test_case.skip_condition(psu):
        pytest.skip(f"{test_case.test_name} not supported by this PSU")
        
    cmd_func = getattr(psu_env["scenario"].commands, test_case.test_name)
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

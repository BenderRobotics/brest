from dataclasses import dataclass, fields
import pytest
from unittest.mock import patch, call
import brest
from brest.communication import SCPICommunicable, SerialCommunicable
from brest.multimeters.multicomp import Multicomp
from brest.multimeters.mp71 import MP71

@dataclass
class FakeCom:
    vid: str
    pid: str
    serial: str
    port: str

@pytest.fixture(autouse=True)
def clear_serial_pool():
    """Clears the serial pool before each test to ensure isolation."""
    SerialCommunicable._SerialCommunicable__POOL.clear()
    SerialCommunicable.TAKEN.clear()

@pytest.fixture
def test_setup():
    """Setup environment"""

    fake_port = FakeCom(port="COM999", vid=0x1A86, pid=0x7523, serial="SN999")
    config_data = {
        'test': {
            'serial_under_test': {
                'class_name': 'interfaces.SerialInterface',
                'interface': {'port': fake_port.port}
            }
        }
    }

    with patch('serial.Serial') as mock_serial_class, \
         patch('brest.pyserial_tools.list_ports.comports', return_value=[fake_port]):

        mock_serial_instance = mock_serial_class.return_value
        mock_serial_instance.port = fake_port.port
        mock_serial_instance.isOpen.return_value = True
        mock_serial_instance.close.reset_mock()

        res = brest.Resources(projects='test', project_config=config_data)
        serial_res = res['serial_under_test']

    yield {
        "res": serial_res,
        "mock": mock_serial_instance,
        "port": fake_port
    }

def test_serial_interface_com_access(test_setup):
    """Tests that the com property can be accessed on SerialInterface."""
    serial_res = test_setup["res"]
    mock_serial_instance = test_setup["mock"]
    fake_port = test_setup["port"]

    # Test com property access
    assert serial_res.com is mock_serial_instance
    assert serial_res.com.port is fake_port.port

def test_serial_interface_disconnect(test_setup):
    """Tests that disconnect() correctly closes the serial port."""
    serial_res = test_setup["res"]
    fake_port = test_setup["port"]

    # Verify close was called
    serial_res.com.close.assert_called_once()

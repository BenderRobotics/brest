import pytest
from unittest.mock import patch, MagicMock
import brest
from brest.loads.tenma import Tenma
from brest.communication import SerialCommunicable, SCPICommunicable

def test_load_validation():
    # Setup configuration with required/default sections for loads
    config_data = {
        'test_project': {
            'load_under_test': {
                'class_name': 'loads.Tenma',
                'required': {
                    'voltage_range': [0.0, 100.0],
                    'protection': ['OVP', 'OCP'],
                    'mode': ['CC', 'CV', 'DYNAMIC_CV']
                },
                'default': {
                    'model': 'TENMA 72-13210',
                    'mode': 'DYNAMIC_CV'
                }
            }
        }
    }

    fake_ports = [
        MagicMock(port='COM999', vid=0x0416, pid=0x5011, serial_number='SN999')
    ]
    
    with patch('serial.Serial') as mock_serial_class, \
         patch('brest.pyserial_tools.list_ports.comports', return_value=fake_ports), \
         patch.object(SerialCommunicable, 'get_connections', return_value=fake_ports), \
         patch.object(SCPICommunicable, 'read_raw', return_value=b"TENMA 72-13210\n"):
         
         # Mock serial instance open check
         mock_serial_instance = mock_serial_class.return_value
         mock_serial_instance.port = 'COM999'
         mock_serial_instance.isOpen.return_value = True
         
         # Instantiate via brest.Resources
         res = brest.Resources(projects='test_project', project_config=config_data)
         
         assert 'load_under_test' in res
         load = res['load_under_test']
         
         # Check that the model applied successfully
         assert load.IDN == 'TENMA 72-13210'
         assert load.MAX_VOLTAGE == 120.0
         assert load.MAX_CURRENT == 30.0
         
         # Release resource
         load.disable_on_destruct = False
         load.release()

def test_load_validation_unsupported_mode():
    config_data = {
        'test_project': {
            'load_under_test': {
                'class_name': 'loads.Tenma',
                'required': {
                    'mode': ['CC', 'DYNAMIC_CV', 'OPP']  # OPP is not in the Tenma model supported_modes
                },
                'default': {
                    'model': 'TENMA 72-13210'
                }
            }
        }
    }
    
    fake_ports = [
        MagicMock(port='COM999', vid=0x0416, pid=0x5011, serial_number='SN999')
    ]
    
    with patch('serial.Serial') as mock_serial_class, \
         patch('brest.pyserial_tools.list_ports.comports', return_value=fake_ports), \
         patch.object(SerialCommunicable, 'get_connections', return_value=fake_ports), \
         patch.object(SCPICommunicable, 'read_raw', return_value=b"TENMA 72-13210\n"):
         
         mock_serial_instance = mock_serial_class.return_value
         mock_serial_instance.port = 'COM999'
         mock_serial_instance.isOpen.return_value = True
         
         # Instantiate should raise SystemExit due to failing requirements
         with pytest.raises(SystemExit):
             brest.Resources(projects='test_project', project_config=config_data)

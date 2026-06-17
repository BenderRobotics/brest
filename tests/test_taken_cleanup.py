"""
    brest.tests.test_taken_cleanup
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Test resource TAKEN clean-up upon failure.
"""

import unittest
from unittest.mock import patch, MagicMock
import brest
from brest.communication import SerialCommunicable, SCPICommunicable
from serial import SerialException

class FakeCom:
    def __init__(self, port, vid, pid, serial_number):
        self.port = port
        self.device = port
        self.vid = vid
        self.pid = pid
        self.serial_number = serial_number


class TestResourceTakenCleanup(unittest.TestCase):
    def setUp(self):
        # Clear serial pool and taken list to start clean
        SerialCommunicable._SerialCommunicable__POOL.clear()
        SerialCommunicable.TAKEN.clear()

    def test_taken_cleanup_on_failure(self):
        """
        Scenario:
        1. Have N needed resources.
        2. One of the resources is not available -> fail -> raises SystemExit (1)
        3. Other successfully initialized resources must be released and unmarked as TAKEN.
        """
        config_data = {
            'test_project': {
                'psu1': {
                    'class_name': 'supplies.Tenma',
                    'interface': {'port': 'COM1', 'vid': 0x0416, 'pid': 0x5011, 'serial_number': 'SN1'}
                },
                'psu2': {
                    'class_name': 'supplies.Tenma',
                    'interface': {'port': 'COM2', 'vid': 0x0416, 'pid': 0x5011, 'serial_number': 'SN2'}
                },
                'psu3': {
                    'class_name': 'supplies.Tenma',
                    'interface': {'port': 'COM3', 'vid': 0x0416, 'pid': 0x5011, 'serial_number': 'SN3'}
                }
            }
        }

        # Mock comport return values (only COM1 and COM2 are present, COM3 is missing!)
        fake_ports = [
            FakeCom('COM1', 0x0416, 0x5011, 'SN1'),
            FakeCom('COM2', 0x0416, 0x5011, 'SN2'),
        ]

        constructed = []
        original_construct = brest.ResourceProvider._construct

        # Hold references to recreate scenarios where the garbage collector does not automatically release them
        def persistent_construct(instance_self, module_name, params):
            res_instance = original_construct(instance_self, module_name, params)
            if res_instance:
                constructed.append(res_instance)  # Keep reference alive!
            return res_instance

        with patch('serial.Serial') as mock_serial_class, \
            patch('brest.pyserial_tools.list_ports.comports', return_value=fake_ports), \
            patch.object(SerialCommunicable, 'get_connections', return_value=fake_ports), \
            patch.object(SCPICommunicable, 'read_raw', return_value=b"TENMA 72-2535"), \
            patch.object(brest.ResourceProvider, '_construct', side_effect=persistent_construct, autospec=True):

            # Setup mock serial instances
            mock_serial_instance1 = MagicMock()
            mock_serial_instance1.port = 'COM1'
            mock_serial_instance1.isOpen.return_value = True

            mock_serial_instance2 = MagicMock()
            mock_serial_instance2.port = 'COM2'
            mock_serial_instance2.isOpen.return_value = True

            def serial_side_effect(port=None, **kwargs):
                if port == 'COM1':
                    return mock_serial_instance1
                if port == 'COM2':
                    return mock_serial_instance2

                # Raise exception on COM3
                raise SerialException(f"Device configured on port {port} is not available.")
            
            mock_serial_class.side_effect = serial_side_effect

            with self.assertRaises(SystemExit) as ex:
                brest.Resources(projects='test_project', project_config=config_data)

            self.assertEqual(ex.exception.code, 1)

            # Check that SerialCommunicable.TAKEN empty
            self.assertEqual(len(SerialCommunicable.TAKEN), 0, f"TAKEN was not cleaned up: {SerialCommunicable.TAKEN}")
            
            # Verify that each resource was released (either via .release() or __del__ method)
            mock_serial_instance1.close.assert_called()
            mock_serial_instance2.close.assert_called()

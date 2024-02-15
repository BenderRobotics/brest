"""
    brest.tests.test_init
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2023 Bender Robotics
"""
import __init__

import logging
import unittest

from brest import Config, find_available_resource
from brest.communication import SerialCommunicable

from unittest.mock import patch


class TestInit(unittest.TestCase):
    """
    The test verifies correct working of functions defined in `__init__.py`.
    """
    @classmethod
    def setUpClass(cls):
        cls.log = logging.getLogger()
        cls.log.info(" Testing functions in __init__.py ".center(100, '='))

    @classmethod
    def tearDownClass(cls):
        cls.log.info("All tests completed.")

    @patch.object(SerialCommunicable, 'probe')
    @patch.object(Config, 'merge_configs', spec=True)
    def test_find_available_resource(self, mock_merge_configs, mock_probe):
        """
        The test verifies that the function find_available_resource() works as it is expected.

        Cases which are tested:
            - set project is not found in config file
            - set resource is not found in config file
            - not specific device name in the config file
            - incorrect interface in config file
            - set project, resource and config file are correct
        """
        self.log.info(" Tested function: find_available_resource() ".center(100, '-'))
        cfg = {
            'project2': {
                'psu': {
                    'class_name': 'Supplies.Tenma',
                    'interface': {
                        'serial_number': '0000'
                    }
                }
            }
        }
        dummy_merged_config1 = Config('project1', config_dict=cfg)
        mock_merge_configs.return_value = dummy_merged_config1

        # invalid project
        msg = "1): set project is not found in config file"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            found_resource = find_available_resource('project1', 'psu')
            self.assertIsNone(
                found_resource,
                msg=(
                    "Method find_available_resource() does not work as it is expected. "
                    f"Expected result: None, obtained result: {found_resource}"
                )
            )
            self.log.info("Test result: OK")

        # bypass first check
        dummy_merged_config1 = Config('project2', config_dict=cfg)
        mock_merge_configs.return_value = dummy_merged_config1

        # invalid resource
        msg = "2): set resource is not found in config file"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            found_resource = find_available_resource('project2', 'bender')
            self.assertIsNone(
                found_resource,
                msg=(
                    "Method find_available_resource() does not work as it is expected. "
                    f"Expected result: None, obtained result: {found_resource}"
                )
            )
            self.log.info("Test result: OK")

        # non-specific device name
        msg = "3): not specific device name in the config file"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            dummy_merged_config1.config = {'psu': {'class_name': 'Supplies'}}
            found_resource = find_available_resource('project2', 'psu')
            self.assertIsNone(found_resource, msg="Method find_available_resource() does not work as it is expected. " \
                                                 f"Expected result: None, obtained result: {found_resource}")
            self.log.info("Test result: OK")

        # # config with incorrect interface
        msg = "4): incorrect interface in config file"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            mock_probe.return_value = []
            dummy_merged_config1.config = {
                'psu': {
                    'class_name': 'Supplies.Tenma',
                    'interface': {
                        'serial_number': '0000'
                    }
                }
            }
            found_resource = find_available_resource('project2', 'psu')
            self.assertIsNone(
                found_resource,
                msg=(
                    "Method find_available_resource() does not work as it is expected. "
                    f"Expected result: None, obtained result: {found_resource}"
                )
            )
            self.log.info("Test result: OK")

        # all params set correctly
        msg = "5): set project, resource and config file are correct"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            mock_probe.return_value = [{'serial_number': '0000'}]
            expected_resource = dummy_merged_config1.config['psu']['class_name']
            found_resource = find_available_resource('project2', 'psu')
            print(found_resource)
            print(expected_resource)
            self.assertEqual(
                found_resource['class_name'],
                expected_resource,
                msg=(
                    "Method find_available_resource() does not work as it is expected. "
                    f"Expected result: {expected_resource}, obtained result: {found_resource}"
                )
            )
            self.log.info("Test result: OK")


if __name__ == '__main__':
    import io
    import sys

    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, failfast=False)
    tp = unittest.main(testRunner=runner, exit=False)

    # log the results
    stream.seek(0)  # Set the pointer to the beginning of the file
    log = logging.getLogger()

    if len(tp.result.errors) > 0:
        log.error(stream.read())
    elif len(tp.result.failures) > 0:
        log.warning(stream.read())
    else:
        log.info(stream.read())

    # exit with error if testing not successful
    if not tp.result.wasSuccessful():
        sys.exit(1)

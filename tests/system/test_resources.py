import unittest
import logging
import brest
import yaml
import pytest

@pytest.fixture(scope="class", autouse=True)
def _inject_needed_option(request, pytestconfig):
    request.cls.cli_needed = pytestconfig.getoption("needed")

class BrestResourceLifecycleTest(unittest.TestCase):
    """
    Test brest.Resources lifecycle: instantiation, resource allocation, and release.
    
    This test suite dynamically adapts its assertions based on the provided `--needed` argument 
    based on the _CONFIG_PATH configuration file. It assumes there isn't another brest session 
    which would interfere with the test execution.
    """
    _CONFIG_PATH = './tests/system/configs/full_config.yml'

    def setUp(self):
        """Prepare loggers and mock configuration structures before every test execution."""
        self.logger = logging.getLogger('brest.test')
        with open(self._CONFIG_PATH, 'r') as file:
            self.mock_project_config = yaml.safe_load(file)

        self.project_name = list(self.mock_project_config.keys())[0]
        self.project_resources_dict = self.mock_project_config[self.project_name]

        if self.cli_needed:
            if isinstance(self.cli_needed, str):
                needed_list = [item.strip() for item in self.cli_needed.split(",")]
            else:
                needed_list = self.cli_needed
        else:
            # Filter out structural YAML keys like 'needed' from the user-facing cheat sheet
            available_hardware = [k for k in self.project_resources_dict.keys()]
            self.skipTest(
                f"Specify needed resources for the system test with --needed=psu_tenma,... "
                f"Available devices: {available_hardware}"
            )

        self.defined_devices = [d for d in needed_list if d in self.project_resources_dict.keys()]
        
        if not self.defined_devices:
            self.skipTest(f"None of the targeted devices {needed_list} exist inside {self._CONFIG_PATH}")


    def test_00_initial_state_empty_taken(self):
        """Assert that an uninstantiated resource pool tracks zero active items."""
        resources = brest.Resources(user_config=None)
        try:
            self.assertEqual(len(resources), 0, "Resource pool should start empty.")
            self.assertEqual(len(resources._resources), 0)
        finally:
            resources.release_all()

    def test_01_full_project_instantiation(self):
        """Verify that passing no 'needed' argument instantiates all config resources."""
        res = brest.Resources(
            projects=self.project_name, 
            project_config=self.mock_project_config,
            user_config=None,
            needed=self.defined_devices
        )

        try:
            self.assertEqual(len(res), len(self.defined_devices), f"Should have instantiated all {len(self.defined_devices)} defined resources.")

            for device in self.defined_devices:
                self.assertIn(device, res.keys(), f"Device {device} failed to instantiate from config.")
        finally:
            res.release_all()

    def test_02_needed_filter_single_resource(self):
        """Verify that 'needed' constraint restricts instantiation exclusively to the first available config device."""
        if not self.defined_devices:
            self.skipTest("No devices found in configuration to test filtering.")
            
        target_device = self.defined_devices[0] 
        needed_resources = [target_device]
        
        res = brest.Resources(
            projects=self.project_name,
            project_config=self.mock_project_config,
            needed=needed_resources
        )

        try:
            self.assertEqual(len(res), 1)
            self.assertIn(target_device, res.keys())
            
            for alternative_device in self.defined_devices[1:]:
                self.assertNotIn(alternative_device, res.keys())
        finally:
            res.release_all()

    def test_03_needed_filter_empty_list(self):
        """Verify that providing an empty list to 'needed' results in zero initialized items."""
        res = brest.Resources(
            projects=self.project_name,
            project_config=self.mock_project_config,
            needed=[]
        )

        try:
            self.assertEqual(len(res), 0, "No resources should be tracked when 'needed' is empty.")
            self.assertFalse(bool(res._resources))
        finally:
            res.release_all()

    def test_04_needed_filter_invalid_resource_raises_exit(self):
        """Verify that requesting a nonexistent class identifier aborts execution via SystemExit."""
        bad_request = ['supplies.FakeDevice']

        with self.assertRaises(SystemExit):
            brest.Resources(
                projects=self.project_name,
                project_config=self.mock_project_config,
                needed=bad_request
            )

    def test_05_needed_filter_multiple_resources(self):
        """Verify that 'needed' constraint restricts instantiation exclusively to up to 2 requested devices found in config."""
        if len(self.defined_devices) < 2:
            self.skipTest("At least 2 defined resources in config are needed to execute this test.")

        # Dynamically take the first two available hardware names
        needed_resources = self.defined_devices[:2]
        ignored_resources = self.defined_devices[2:]
        
        res = brest.Resources(
            projects=self.project_name,
            project_config=self.mock_project_config,
            user_config=None,
            needed=needed_resources
        )

        try:
            self.assertEqual(len(res), 2, "The 'needed' filter should limit allocation to exactly 2 resources.")
            for device in needed_resources:
                self.assertIn(device, res.keys(), f"Requested device '{device}' was not instantiated.")

            for device in ignored_resources:
                self.assertNotIn(device, res.keys(), f"Device '{device}' should have been ignored by filtering rules.")
        finally:
            res.release_all()

    def test_06_release_all_clears_pool(self):
        """Assert that release_all tears down active handles, clear aliases, and internal maps."""
        target_device = self.defined_devices[0] 
        needed_resources = [target_device]

        res = brest.Resources(
            projects=self.project_name,
            project_config=self.mock_project_config,
            needed=needed_resources
        )

        try:
            self.assertTrue(len(res._resources) > 0)
            print(res._resources)
            res.release_all()

            self.assertEqual(len(res._resources), 0, "Active resource mappings were not flushed.")
            self.assertEqual(len(res._aliases_mappings), 0, "Active alias index rules were not flushed.")
        finally:
            res.release_all()

    def test_07_get_taken_contents(self):
        """Extract config properties dynamically and assert get_taken() schema structure."""
        if not self.defined_devices:
            self.skipTest("No hardware configurations to target sample request.")

        # Grab a target device and look up its actual class path from the YAML config
        target_device = self.defined_devices[0]
        expected_class = self.project_resources_dict[target_device].get('class_name', '')

        res = brest.Resources(
            projects=self.project_name,
            project_config=self.mock_project_config,
            user_config=None,
            needed=[target_device]
        )

        try:
            device_instance = res[target_device]
            taken_list = res.get_taken()
            
            self.assertIsInstance(taken_list, list)
            self.assertEqual(len(taken_list), 1, "The chosen resource should appear in get_taken().")

            matched_taken_device = False
            for entry in taken_list:
                self.assertIn('resource', entry)
                self.assertIn('interface', entry)

                # Dynamically match against the exact string value parsed out of the configuration file
                if expected_class in str(entry['resource']):
                    matched_taken_device = True

            self.assertTrue(matched_taken_device, f"Could not find an active taken device matching class '{expected_class}' ({device_instance}).")
        finally:
            res.release_all()

    def test_08_get_all_contents(self):
        """Verify compound get_all() schema maps ('taken' and 'available') via variable config hooks."""
        if len(self.defined_devices) < 2:
            self.skipTest("Requires at least 2 config resources to test both taken and available divisions.")
            self.fail()
        # Take the 1st item, leave the rest as 'available'
        target_device = self.defined_devices[0]
        expected_taken_class = self.project_resources_dict[target_device].get('class_name', '')
        
        expected_available_classes = [
            self.project_resources_dict[dev].get('class_name', '') for dev in self.defined_devices[1:]
        ]

        res = brest.Resources(
            projects=self.project_name,
            project_config=self.mock_project_config,
            user_config=None,
            needed=[target_device]
        )

        try:
            all_data = res.get_all()
            
            self.assertIsInstance(all_data, dict)
            self.assertIn('taken', all_data)
            self.assertIn('available', all_data)
            
            self.assertTrue(len(all_data['taken']) > 0, "There should be at least 1 device in the taken block.")
            
            # Confirm the selected item is marked as taken
            taken_match = any(expected_taken_class in str(item['resource']) for item in all_data['taken'])
            self.assertTrue(taken_match, f"The requested '{expected_taken_class}' was not found in the 'taken' partition.")

            # Confirm that all non-selected items are listed in the available pool
            self.assertTrue(len(all_data['available']) > 0, "Idle resources should populate the available section.")
            
            # Flatten out all available class names coming back from the live registry state
            live_available_classes = []
            for item in all_data['available']:
                # Handle cases if class_name is a list or a raw string
                classes = item['class_name']
                if isinstance(classes, list):
                    live_available_classes.extend(classes)
                else:
                    live_available_classes.append(classes)

            # Ensure every skipped item in the config file is accounted for in the live available stack
            for expected_avail in expected_available_classes:
                self.assertIn(
                    expected_avail, 
                    live_available_classes, 
                    f"Configuration resource class '{expected_avail}' is missing from the available resources pool!"
                )
        finally:
            res.release_all()

if __name__ == "__main__":
    unittest.main(verbosity=2)
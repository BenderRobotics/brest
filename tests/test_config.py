"""
    brest.tests.test_config
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2024 Bender Robotics
"""
import conftest

import logging
import unittest

from brest.config import Config


class TestConfig(unittest.TestCase):
    """
    The test verifies correct working of methods defined in Config().
    """

    @classmethod
    def setUpClass(cls):
        cls.log = logging.getLogger('test')
        cls.log.info(" Testing methods in brest.config.Config() ".center(100, '='))

    @classmethod
    def tearDownClass(cls):
        cls.log.info("All tests completed.")

    def test_config(self):
        """
        The test verifies correct Config initialization.

        Cases which are tested:
            - valid config file
            - creating config from a dict
            - creating config from a dict
        """
        self.log.info(" Tested function: Config() (config constructor)".center(100, '-'))

        msg = "1): creating config from a valid config file - one project as input"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1']
            config1 = Config(projects=projects, config_path="tests/dummy_files/dummy_config_valid.yaml")
            self.assertNotIn('project1', config1.config)
            self.assertIn('psu', config1.config)
            self.assertNotIn('project2', config1.config)
            self.assertNotIn('switch', config1.config)
            self.log.info("Test result: OK")

        msg = "2): creating config from a valid config file - multiple projects as input"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1', 'project2']
            config1 = Config(projects=projects, config_path="tests/dummy_files/dummy_config_valid.yaml")
            self.assertNotIn('project1', config1.config)
            self.assertIn('psu', config1.config)
            self.assertNotIn('project2', config1.config)
            self.assertIn('switch', config1.config)
            self.log.info("Test result: OK")

        msg = "3): creating config from an invalid config file"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            with self.assertRaises(SystemExit):
                config1 = Config(config_path="tests/dummy_files/dummy_config_invalid_parsing.yaml")
            self.log.info("Test result: OK")

        msg = "4): creating config from a valid config dict"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            dummy_config_dict={
                'project1': {
                    'psu': {
                        'class_name': 'supplies.Tenma',
                        'default': {
                            'voltage': 20,
                            'current': 0.2,
                            'protection': 'OCP'
                        },
                        'interface': {
                            'serial_number': '0123456789'
                        }
                    }
                }
            }
            config1 = Config(config_dict=dummy_config_dict)
            self.assertNotIn('project1', config1.config)
            self.assertNotIn('psu', config1.config)
            self.log.info("Test result: OK")

        msg = "5): creating config from a valid config file - merge devs of multiple projects"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1', 'project2']
            config1 = Config(projects=projects, config_path="tests/dummy_files/dummy_multiple_devs_projects.yaml")
            self.assertNotIn('project1', config1.config)
            self.assertIn('psu_ext', config1.config)
            self.assertNotIn('project2', config1.config)
            self.assertIn('engine', config1.config)
            self.log.info("Test result: OK")

        msg = "6): creating empty config from a non-existed config file"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project']
            config1 = Config(projects=projects, config_path="tests/dummy_files/nonexisted.yaml")
            self.assertDictContainsSubset(config1.config, {})
            self.log.info("Test result: OK")

    def test_config_is_valid(self):
        """
        The test verifies correct config validation.

        Cases which are tested:
            - valid config - projects match
            - no projects specified
            - projects dont match
        """
        self.log.info(" Tested property: is_valid ".center(100, '-'))

        msg = "1): valid config - contaings the project specified in `projects`"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1']
            config1 = Config(projects=projects, config_path="tests/dummy_files/dummy_config_valid.yaml")
            self.assertTrue(config1.is_valid)
            self.log.info("Test result: OK")

        msg = "2): Invalid config - no projects specified"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            config1 = Config(projects=[], config_path="tests/dummy_files/dummy_config_valid.yaml")
            self.assertFalse(config1.is_valid)
            self.log.info("Test result: OK")

        msg = "3): Invalid config - does not contain the project specified in `projects`"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1']
            dummy_config_dict = {
                'project2': {
                    'psu': {
                        'class_name': 'supplies.Tenma',
                        'default': {
                            'voltage': 20,
                            'current': 0.2,
                            'protection': 'OCP'
                        },
                        'interface': {
                            'serial_number': '0123456789'
                        }
                    }
                }
            }
            config1 = Config(projects=projects, config_dict=dummy_config_dict)
            self.assertFalse(config1.is_valid)
            self.log.info("Test result: OK")

        msg = "4): Valid config - after merging of the multiple configs"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1', 'project2']
            dummy_dict1 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_dict2 = {
                'project1': {
                    'relay': {
                        'class_name': 'IO.Manio'
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            self.assertFalse(dummy_config1.is_valid)
            self.assertFalse(dummy_config2.is_valid)
            result = dummy_config2.merge_configs(dummy_config1)
            self.assertTrue(
                result.is_valid,
                msg=(
                    f"Expected '{projects}'; "
                    f"result.required_projects:'{result.required_projects}', "
                    f"result.contained_projects:'{result.contained_projects}', "
                    f"result.raw_config:'{result.raw_config}'"
                )
            )
            self.log.info("Test result: OK")

        msg = "5): Valid config - after merging of the multiple configs"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project2']
            dummy_dict1 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            projects = ['project1', 'project2']
            dummy_dict2 = {
                'project1': {
                    'relay': {
                        'class_name': 'IO.Manio'
                    }
                }
            }
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            self.assertTrue(dummy_config1.is_valid)
            self.assertFalse(dummy_config2.is_valid)
            result = dummy_config2.merge_configs(dummy_config1)
            self.assertTrue(result.is_valid)
            self.log.info("Test result: OK")

        msg = "6): Invalid config - after merging of the multiple configs"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project3']
            dummy_dict1 = {
                'project3': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            projects = ['project1', 'project2', 'project3']
            dummy_dict2 = {
                'project1': {
                    'relay': {
                        'class_name': 'IO.Manio'
                    }
                }
            }
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            self.assertTrue(dummy_config1.is_valid)
            self.assertFalse(dummy_config2.is_valid)
            result = dummy_config2.merge_configs(dummy_config1)
            self.assertFalse(result.is_valid)
            self.log.info("Test result: OK")

    def test_merge_configs(self):
        """
        The test verifies that the method merge_config() works as it is expected.

        Cases which are tested:
            - projects in config files are different
            - projects in config files are the same
            - one of the config files is empty
            - one of the configs is tampered with before merging
        """
        self.log.info(" Tested function: merge_configs() ".center(100, '-'))

        # projects in config files are diffrent
        msg = "1): projects in config files are different"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1', 'project2']
            dummy_dict1 = {
                'project1': {
                    'relay': {
                        'class_name': 'IO.Manio'
                    }
                }
            }
            dummy_dict2 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertDictContainsSubset(dummy_dict1['project1'], result.config)
            self.assertDictContainsSubset(dummy_dict2['project2'], result.config)
            self.log.info("Test result: OK")

        # projects in config files are the same
        msg = "2): projects in config files are the same"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1']
            dummy_dict1 = {
                'project1': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_dict2 = {
                'project1': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertDictContainsSubset(dummy_config1.config, result.config)
            self.log.info("Test result: OK")

        # config file 1 is empty
        msg = "3): one of the config files is empty"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project2']
            dummy_dict1 = {}
            dummy_dict2 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma', 'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            result = dummy_config2.merge_configs(dummy_config1)
            print(result)
            self.assertEqual(dummy_config2.config, result.config)
            self.log.info("Test result: OK")

        # config file 2 is empty
        msg = "4): one of the config files is empty"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project2']
            dummy_dict1 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma', 'disable_on_destruct': False
                    }
                }
            }
            dummy_dict2 = {}
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            result = dummy_config2.merge_configs(dummy_config1)
            print(result)
            self.assertEqual(dummy_config1.config, result.config)
            self.log.info("Test result: OK")

        # projects in config files are almost the same
        msg = "5): projects in config files are almost the same"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project2']
            dummy_dict1 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma', 'disable_on_destruct': False
                    }
                }
            }
            dummy_dict2 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': True
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            result = dummy_config2.merge_configs(dummy_config1)
            print(result)
            self.assertEqual(dummy_config1.config, result.config)
            self.log.info("Test result: OK")

        # anti-tamper check: new config
        msg = "6): new config has been tampered with before merging"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1', 'project2']
            dummy_dict1 = {
                'project1': {
                    'relay': {
                        'class_name': 'IO.Manio'
                    }
                }
            }
            dummy_dict2 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config1.config['relay']['interface'] = 'iface1'
            dummy_config2 = Config(projects, config_dict=dummy_dict2)

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertListEqual(['custom', 'project1', 'project2'], result.required_projects)
            self.assertDictContainsSubset(dummy_dict1['project1'], result.config)
            self.assertDictContainsSubset(dummy_dict2['project2'], result.config)
            self.assertIn('interface', result.config['relay'])
            self.assertEqual(result.config['relay']['interface'], 'iface1')
            self.log.info("Test result: OK")

        # anti-tamper check: current config
        msg = "7): current config has been tampered with before merging"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1', 'project2']
            dummy_dict1 = {
                'project1': {
                    'relay': {
                        'class_name': 'IO.Manio'
                    }
                }
            }
            dummy_dict2 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config2 = Config(projects, config_dict=dummy_dict2)
            dummy_config2.config['lamp'] = {
                'bulb': {
                    'status': 'on'
                }
            }

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertListEqual(['custom', 'project1', 'project2'], result.required_projects)
            self.assertDictContainsSubset(dummy_dict1['project1'], result.config)
            self.assertDictContainsSubset(dummy_dict2['project2'], result.config)
            self.assertIn('lamp', result.config)
            self.assertIn('bulb', result.config['lamp'])
            self.assertIn('status', result.config['lamp']['bulb'])
            self.assertEqual(result.config['lamp']['bulb']['status'], 'on')
            self.log.info("Test result: OK")

        # anti-tamper check: handling of already existing "custom" keyword
        msg = "8): both configs have been tampered with and there already is 'custom' keyword present"
        self.log.info(f"Test case {msg}")
        with self.subTest(test_case=msg):
            projects = ['project1', 'project2']
            dummy_dict1 = {
                'project1': {
                    'relay': {
                        'class_name': 'IO.Manio'
                    }
                },
                'custom': {
                    'stuff': 'yes'
                }
            }
            dummy_dict2 = {
                'project2': {
                    'psu': {
                        'class_name': 'Supplies.Tenma',
                        'disable_on_destruct': False
                    }
                }
            }
            dummy_config1 = Config(projects, config_dict=dummy_dict1)
            dummy_config1.config['lamp'] = 'on'
            dummy_config2 = Config(projects, config_dict=dummy_dict2)
            dummy_config2.config['lamp'] = 'off'

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertRegex(result.required_projects[0], r'custom[0-9]+')
            self.assertEqual('project1', result.required_projects[1])
            self.assertEqual('project2', result.required_projects[2])
            self.assertDictContainsSubset(dummy_dict1['project1'], result.config)
            self.assertDictContainsSubset(dummy_dict2['project2'], result.config)
            self.assertIn('lamp', result.config)
            self.assertEqual(result.config['lamp'], 'on')
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

"""
    brest.tests.test_config
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2023 Bender Robotics
"""
import __init__

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

    def test_merge_configs(self):
        """
        The test verifies that the method merge_config() works as it is expected.

        Cases which are tested:
            - projects in config files are different
            - projects in config files are the same
            - one of the config files is empty
        """
        self.log.info(" Tested function: merge_configs() ".center(100, '-'))
        dummy_config1 = Config()
        dummy_config2 = Config()

        # projects in config files are diffrent
        self.log.info("1) Test case: projects in config files are different")
        with self.subTest(test_case='different projects in config files'):
            dummy_config1.config = {'project1': 'switch'}
            dummy_config2.config = {'project2': {'psu': {'class_name': 'Supplies.Tenma', 'disable_on_destruct': False}}}

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertDictContainsSubset(dummy_config1.config, result.config)
            self.assertDictContainsSubset(dummy_config2.config, result.config)
            self.log.info("Test result: OK")

        # projects in config files are the same
        self.log.info("2) Test case: projects in config files are the same")
        with self.subTest(test_case='same projects in config files'):
            dummy_config1.config = {'project2': 'switch'}
            dummy_config2.config = {'project2': {'psu': {'class_name': 'Supplies.Tenma', 'disable_on_destruct': False}}}

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertEqual(dummy_config1.config, result.config)
            self.log.info("Test result: OK")

        # config file is empty
        self.log.info("3) Test case: one of the config files is empty")
        with self.subTest(test_case='empty config file'):
            dummy_config1.config = {}
            dummy_config2.config = {'project2': {'psu': {'class_name': 'Supplies.Tenma', 'disable_on_destruct': False}}}

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertEqual(dummy_config2.config, result.config)
            self.log.info("Test result: OK")

        # config file is empty
        self.log.info("4) Test case: one of the config files is empty")
        with self.subTest(test_case='empty config file'):
            dummy_config1.config = {'project1': 'switch'}
            dummy_config2.config = {}

            result = dummy_config2.merge_configs(dummy_config1)
            self.assertEqual(dummy_config1.config, result.config)
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

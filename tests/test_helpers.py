"""
    brest.tests.test_helpers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2022 Bender Robotics
"""
import __init__

import logging
import unittest

from brest.helpers import prepare_tests

from unittest.mock import patch
from unittest.loader import _FailedTest


class PrepareTests(unittest.TestCase):
    """
    The test verifies correct working of functions defined in `helpers.py`.
    """

    @classmethod
    def setUpClass(cls):
        cls.log = logging.getLogger()
        cls.log.info(" Testing functions in brest.helpers ".center(100, '='))

    @classmethod
    def tearDownClass(cls):
        cls.log.info("All tests completed.")

    @patch('brest.resources.Resources')
    def test_prepare_tests(self, mock_resources):
        """
        The test verifies that the function prepare_tests() works as it is expected.

        Cases which are tested:
            - tests are loaded correctly
            - tests are not loaded correctly
        """
        self.log.info(" Tested function: prepare_tests() ".center(100, '-'))
        test_suite = unittest.suite.TestSuite()

        # loaded correctly
        self.log.info("1) Test case: tests are loaded correctly")
        with self.subTest(test_case='correct load of the tests'):
            dummy_test_case = unittest.TestCase()
            dummy_test_case._testMethodName = 'test_01'
            setattr(dummy_test_case, 'needed', ['psu'])
            test_suite._tests = [dummy_test_case]

            mock_resources.return_value = True
            resources = prepare_tests(test_suite, 'project1')
            self.assertTrue(resources, msg="Tests are not loaded correctly.")
            self.log.info("Test result: OK")

        # not loaded correctly - syntax error
        self.log.info("2) Test case: tests are not loaded correctly (syntax error)")
        with self.subTest(test_case='syntax error'):
            failed_test = _FailedTest('test_01', 'syntax error')
            test_suite._tests = [failed_test]

            with self.assertRaises(SystemExit):
                prepare_tests(test_suite, 'project1')
            self.log.info("Test result: OK")


if __name__ == '__main__':
    import io

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

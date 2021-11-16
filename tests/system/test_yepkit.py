import brest
import unittest
import logging
from time import sleep

class YepkitTest(unittest.TestCase):
    def setUp(self):
        """Method to prepare the test fixture. Run BEFORE the test methods."""
        self.rp = brest.ResourceProvider()
        self.logger = logging.getLogger('brest')
        self.log_args = {'class_name': self.__class__.__module__ + '.' + self.__class__.__name__}
        # TODO partial method...

    def tearDown(self):
        """Method to tear down the test fixture. Run AFTER the test methods."""
        pass

    def _get_yepkit(self):
        available = self.rp.available()
        yepkit_desc = tuple(r for r in available if r['class_name'].__contains__('Yepkit'))[0]
        yepkit = brest.ResourceProvider().construct(yepkit_desc)
        return yepkit

    def test_00_basic_func(self):
        """Check if brest can discover the device and modify channels"""
        yepkit = self._get_yepkit()

        self.logger.info("Testing channel get/set", extra=self.log_args)

        for i in range(yepkit.CHANNELS):
            with self.subTest(channel=i):
                state_before = yepkit[i]
                self.assertIsInstance(state_before, int)
                yepkit[i] = not state_before
                state_after = yepkit[i]
                self.assertIsInstance(state_after, int)
                self.assertNotEqual(state_before, state_after, "Channel did not change")
                self.logger.info("Channel [%s] ok", i, extra=self.log_args)

    def test_01_bl_version(self):
        yepkit = self._get_yepkit()

        bl_version = yepkit.get_bl_version()

        self.assertRegex(bl_version, r"\d.\d.\d", "Incorrect format of Bl version")
        self.logger.info("Bl version %s", bl_version, extra=self.log_args)

    def test_02_fw_version(self):
        yepkit = self._get_yepkit()

        fw_version = yepkit.get_fw_version()

        self.assertRegex(fw_version, r"\d.\d.\d", "Incorrect format of Fw version")
        self.logger.info("Fw version %s", fw_version, extra=self.log_args)

    def test_03_gpio_func(self):
        yepkit = self._get_yepkit()

        for i in range(yepkit.CHANNELS):
            state_before = yepkit.read_io(i)
            self.assertIsInstance(state_before, int)
            yepkit.write_io(i, not state_before)
            state_after = yepkit.read_io(i)
            self.assertIsInstance(state_after, int)
            self.assertNotEqual(state_before, state_after, "Port did not change")
            self.logger.info("IO[%s] OK", i, extra=self.log_args)

    def test_04_reset_func(self):
        yepkit = self._get_yepkit()

        with self.assertRaises(OSError):
            yepkit.reset()

        sleep(7)  # * wait for USB to reconnect

        self.logger.info("Reset OK", extra=self.log_args)


if __name__ == "__main__":
    import io

    input("Make sure yepkit device is connected to PC ok?")

    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, failfast=False)
    tp = unittest.main(testRunner=runner, exit=False, verbosity=2)

    stream.seek(0)
    print(stream.read())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.cameras.basler
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements Basler camera.

    :copyright: 2022 Bender Robotics
"""

import logging

from brest.cameras import Cameras
from brest.communication import CameraCommunicable


class Basler(Cameras, CameraCommunicable):
    """
    Basler cameras.

    Derived from: :class:`~brest.cameras.Cameras`, :class:`~brest.communication.CameraCommunicable`

    :param params: Construction parameters
    :type  params: dict
    """

    Cameras.KNOWN['Basler'] = {
        'type': 'camera',
        'service': 'plnu3v',
        }

    def __init__(self, params):
        Cameras.__init__(self, params)
        CameraCommunicable.__init__(self, params['interface'])

        self._sw_trigger = True

        try:
            from pypylon import pylon
        except ModuleNotFoundError:
            msg = 'To use {} class you have to install `pypylon` module'.format(self.__class__.__name__)
            raise ModuleNotFoundError(msg)

        # Create factory for interfaces
        tl_factory = pylon.TlFactory.GetInstance()
        available_devices = tl_factory.EnumerateDevices()
        num_cameras = len(available_devices)

        if num_cameras == 0:
            self.logger.error('No Basler camera detected')
        else:
            self._cam = pylon.InstantCamera(tl_factory.CreateDevice(available_devices[params['interface']['index']]))
            self.cam.Open()
            self.cam.PixelFormat.SetValue("BGR8")
            self.cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def __del__(self):
        """
        De-initialize camera
        """
        self.release()

    def release(self):
        """
        Releases the camera
        """
        Cameras.release(self)
        CameraCommunicable.release(self)

        if self._cam is not None:
            self._cam.StopGrabbing()
            self._cam.Close()
            del self._cam

    def configure_trigger(self, trigger):
        """
        This function configures the camera to use a given trigger

        :param trigger: trigger for camera.
        :type  trigger: str
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        from pypylon import genicam

        triggers = {
            'line0': 'Line1',
            'line1': 'Line2',
            'line2': 'Line3',
            'line3': 'Line4',
            'software': 'Software'
        }

        try:
            # Ensure trigger mode off
            if ('TriggerMode' not in dir(self.cam)) or (self.cam.TriggerMode.GetAccessMode() != genicam.RW):
                self.logger.warning('Unable to disable trigger mode, camera does not have TriggerMode property',
                                    extra=self.log_args)
            # Ensure trigger source can be changed
            elif ('TriggerSource' not in dir(self.cam)) or self.cam.TriggerSource.GetAccessMode() != genicam.RW:
                self.logger.warning('Unable to get trigger source, camera does not have TriggerSource property',
                                    extra=self.log_args)
            # Ensure trigger source is supported
            elif trigger not in triggers:
                self.logger.warning('Not supported trigger source: "{}"'.format(trigger), extra=self.log_args)
            # Set the trigger
            else:
                self.cam.TriggerMode.SetValue('On')
                self.cam.TriggerSource.SetValue(triggers[trigger])
                self._sw_trigger = (trigger == 'software')
                return True
        except Exception as ex:
            self.logger.error('Error occurred during trigger configuration: {}'.format(str(ex)), extra=self.log_args)

        return False

    def configure_exposure(self, exposure_time):
        """
        This function configures a custom exposure time. Automatic exposure is turned
        off in order to allow for the customization, and then the custom setting is
        applied.

        :param exposure_time: exposure time value [ms], 0 for continuous
        :type  exposure_time: float
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        from pypylon import genicam

        try:
            result = True

            # Set Exposure mode to Timed
            if ('ExposureTimed' not in dir(self.cam)) or (self.cam.ExposureMode.GetAccessMode() != genicam.RW):
                msg = 'Unable to set timed exposure mode'\
                      ', camera doesnot have ExposureMode property or it is not writable'
                self.logger.warning(msg, extra=self.log_args)
                return False

            self.cam.ExposureMode.SetValue('Timed')

            # Try to disabe automatic exposure mode
            if ('ExposureAuto' not in dir(self.cam)) or (self.cam.ExposureAuto.GetAccessMode() != genicam.RW):
                msg = 'Unable to disable automatic exposure'\
                      ', camera does not have ExposureAuto property or it is not writable'
                self.logger.warning(msg, extra=self.log_args)
                return False

            # Exposure time == 0 -> Continuous
            if not exposure_time:
                self.cam.ExposureAuto.SetValue('Continuous')
            else:
                self.cam.ExposureAuto.SetValue('Off')
                exposure_time = int(exposure_time * 1000)  # [ms] to [us]

                # Ensure desired exposure time does not exceed limits
                if ('AutoExposureTimeUpperLimit' not in dir(self.cam)) or \
                   (self.cam.AutoExposureTimeUpperLimit.GetAccessMode() != genicam.RW):
                    msg = 'Unable to get autoexposure max limit'\
                        ', camera does not have AutoExposureTimeUpperLimit property or it is not writable'
                    self.logger.warning(msg, extra=self.log_args)
                else:
                    exposure_time = min(self.cam.AutoExposureTimeUpperLimit.GetMax(), exposure_time)

                if ('AutoExposureTimeLowerLimit' not in dir(self.cam)) or \
                   (self.cam.AutoExposureTimeLowerLimit.GetAccessMode() != genicam.RW):
                    msg = 'Unable to get autoexposure min limit'\
                          ', camera does not have AutoExposureTimeLowerLimit property or it is not writable'
                    self.logger.warning(mag, extra=self.log_args)
                else:
                    exposure_time = max(self.cam.AutoExposureTimeLowerLimit.GetMin(), exposure_time)

                if ('ExposureTime' not in dir(self.cam)) or (self.cam.ExposureTime.GetAccessMode() != genicam.RW):
                    msg = 'Unable to set exposure time'\
                          ', camera does not have ExposureTime property or it is not writable'
                    self.logger.warning(msg, extra=self.log_args)
                    return False
                self.cam.ExposureTime.SetValue(exposure_time)

        except Exception as ex:
            self.logger.error('Error occurred during exposure configuration: {}'.format(str(ex)), extra=self.log_args)
            result = False

        return result

    def configure_gain(self, gain):
        """
        This function configures a custom gain. Automatic gain is turned
        off in order to allow for the customization, and then the custom setting is
        applied.

        :param gain: gain value
        :type  gain: float
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        from pypylon import genicam

        try:
            result = True
            if ('GainAuto' not in dir(self.cam)) or (self.cam.GainAuto.GetAccessMode() != genicam.RW):
                msg = 'Unable to disable automatic gain, camera does not have GainAuto property or it is not writable'
                self.logger.warning(msg, extra=self.log_args)
                return False
            self.cam.GainAuto.SetValue('Off')

            if ('Gain' not in dir(self.cam)) or (self.cam.Gain.GetAccessMode() != genicam.RW):
                self.logger.warning('Unable to set gain, camera does not have Gain property or it is not writable',
                                    extra=self.log_args)
                return False
            self.cam.Gain.SetValue(gain)

        except Exception as ex:
            self.logger.error('Error occurred during gain configuration: {}'.format(str(ex)), extra=self.log_args)
            result = False

        return result

    def configure_gamma(self, gamma):
        """
        This function configures a custom gamma.

        :param gamma: Gamma value, False set gamma to off
        :type  gamma: float
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        from pypylon import genicam

        try:
            result = True
            if ('Gamma' not in dir(self.cam)) or (self.cam.Gamma.GetAccessMode() != genicam.RW):
                self.logger.warning('Unable to set gamma, camera does not have Gamma property or it is not writable',
                                    extra=self.log_args)
                return False

            if gamma is False:
                self.cam.Gamma.SetValue(1)  # Default
            else:
                # Ensure desired gamma does not exceed the maximum
                gamma = min(self.cam.Gamma.GetMax(), gamma)
                self.cam.Gamma.SetValue(gamma)

        except Exception as ex:
            self.logger.error('Error occurred during gamma configuration: {}'.format(str(ex)), extra=self.log_args)
            result = False

        return result

    def configure_framerate(self, framerate):
        """
        This function configures a custom framerate. Automatic framerate is turned
        off in order to allow for the customization, and then the custom setting is
        applied.

        :param framerate: framerate value [fps]
        :type  framerate: float
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        from pypylon import genicam

        try:
            result = True

            if ('AcquisitionFrameRateEnable' not in dir(self.cam)) or \
               (self.cam.AcquisitionFrameRateEnable.GetAccessMode() != genicam.RW):
                msg = 'Unable to disable automatic framerate'\
                      ', camera does not have AcquisitionFrameRateEnable property or it is not writable'
                self.logger.warning(msg, extra=self.log_args)
                return False

            self.cam.AcquisitionFrameRateEnable.SetValue(True)

            if ('AcquisitionFrameRate' not in dir(self.cam)) or \
               (self.cam.AcquisitionFrameRate.GetAccessMode() != genicam.RW):
                msg = 'Unable to set framerate'\
                      ', camera does not have AcquisitionFrameRate property or it is not writable'
                self.logger.warning(msg, extra=self.log_args)
                return False

            # Ensure desired framerate does not exceed the maximum
            framerate = min(self.cam.AcquisitionFrameRate.GetMax(), framerate)
            self.cam.AcquisitionFrameRate.SetValue(framerate)

        except Exception as ex:
            self.logger.error('Error occurred during framerate configuration: {}'.format(str(ex)), extra=self.log_args)
            result = False

        return result

    def configure_white_auto_balance(self, auto):
        """
        This function set white balance

        :param auto: type of white autobalance (off, once, on)
        :type  auto: string
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        from pypylon import genicam

        result = True

        try:
            if ('BalanceWhiteAuto' not in dir(self.cam)) or (self.cam.BalanceWhiteAuto.GetAccessMode() != genicam.RW):
                msg = 'Unable to configure auto white balance'\
                      ', camera does not have BalanceWhiteAuto property or it is not writable'
                self.logger.warning(msg, extra=self.log_args)
                return False
            if auto.lower() == 'once':
                self.cam.BalanceWhiteAuto.SetValue('Once')
            elif auto.lower() == 'on':
                self.cam.BalanceWhiteAuto.SetValue('Continuous')
            else:
                self.cam.BalanceWhiteAuto.SetValue('Off')
        except Exception as ex:
            self.logger.error('Error occurred during white auto balance configuration: {}'.format(str(ex)),
                              extra=self.log_args)
            result = False

        return result

    def acquire_image(self):
        """
        acquire actual image from camera

        :returns: acquired image
        :rtype: cv2 image (b,g,r matrix)
        """
        from pypylon import pylon

        data = None

        try:
            if self._sw_trigger:
                # trigger frame by software
                if self.cam.WaitForFrameTriggerReady(200, pylon.TimeoutHandling_ThrowException):
                    self.cam.ExecuteSoftwareTrigger()

            self.cam.GetGrabResultWaitObject().Wait(200)
            grab_result = self.cam.RetrieveResult(0, pylon.TimeoutHandling_ThrowException)

            if grab_result.GrabSucceeded():
                self.img_width = grab_result.GetWidth()
                self.img_height = grab_result.GetHeight()
                data = grab_result.GetArray().reshape(self.img_height, self.img_width, 3)

        except Exception as ex:
            self.logger.error('Error occurred during image acquisition configuration: {}'.format(str(ex)),
                              extra=self.log_args)

        return data

    def reset_trigger(self):
        """
        This function returns the camera to a normal state by turning off trigger mode.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """
        from pypylon import genicam

        try:
            if ('TriggerMode' not in dir(self.cam)) or (self.cam.TriggerMode.GetAccessMode() != genicam.RW):
                msg = 'Unable to reset triger mode, camera does not have TriggerMode property or it is not writable'
                self.logger.warning(msg, extra=self.log_args)
                return False
            self.cam.TriggerMode.SetValue('Off')
            return True

        except Exception as ex:
            self.logger.error('Error occurred during trigger reset: {}'.format(str(ex)), extra=self.log_args)

        return False

    def get_info(self):
        """
        This function returns the device information of the camera as a string.

        :returns: info in a string
        :rtype: string
        """
        try:
            from pypylon import genicam
        except ModuleNotFoundError:
            msg = 'To use {} class you have to install `pypylon` module'.format(self.__class__.__name__)
            raise ModuleNotFoundError(msg)

        info = ''

        try:
            device_control = self.cam.DeviceControl
            features = device_control.GetFeatures()

            for feature in features:
                access_mode = feature.GetAccessMode()
                if access_mode in [genicam.RO, genicam.RW]:  # Get value if access mode is Read-Only or Read-Write
                    info += '{}: {}\n'.format(feature.Node.Name, feature.GetValue())
                else:
                    info += '{}: value not available\n'.format(feature.Node.Name)

        except Exception as ex:
            self.logger.error('Error occurred during camera info retrieving: {}'.format(str(ex)))

        if not info:
            info = 'No info available for the device'
        return info

    def detect_model(self):
        """
        """
        pass

    def default_trigger(self, value):
        if not isinstance(value, str):
            self.logger.error('Trigger value must be a string', extra=self.log_args)
            return False
        return self.configure_trigger(value)

    def default_exposure(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            self.logger.error('Exposure value must be a float', extra=self.log_args)
            return False
        return self.configure_exposure(value)

    def default_gain(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            self.logger.error('Gain value must be a float', extra=self.log_args)
            return False
        return self.configure_gain(value)

    def default_gamma(self, value):
        if not isinstance(value, float) and not isinstance(value, bool):
            self.logger.error('Gamma value must be a float or bool', extra=self.log_args)
            return False
        return self.configure_gamma(value)

    def default_framerate(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            self.logger.error('Framerate value must be a float', extra=self.log_args)
            return False
        return self.configure_framerate(value)

    def default_white_auto_balance(self, value):
        if not isinstance(value, str):
            self.logger.error('White auto balance value must be a string', extra=self.log_args)
            return False
        return self.configure_white_auto_balance(value)

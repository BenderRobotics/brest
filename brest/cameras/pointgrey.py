# -*- coding: utf-8 -*-
"""
    brest.cameras.pointgrey
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements PointGrey camera.

    :copyright: 2019 Bender Robotics
"""

import logging

from brest.cameras import Cameras
from brest.communication import CameraCommunicable


class PointGrey(Cameras, CameraCommunicable):
    """
    PointGrey cameras

    :param params: Construction parameters
    :type  params: dict
    """

    Cameras.KNOWN['PointGrey'] = {
        'type': 'camera',
        'service': 'PGRUSBCam3',
        }

    def __init__(self, params):
        Cameras.__init__(self, params)
        CameraCommunicable.__init__(self, params['interface'])

        try:
            import PySpin
        except ModuleNotFoundError:
            raise ModuleNotFoundError('To use {} class you have to install `PySpin` module'.format(self.__class__.__name__))

        # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()

        # Retrieve list of cameras from the system
        cam_list = self.system.GetCameras()
        num_cameras = cam_list.GetSize()

        # Finish if there are no cameras
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()
            self.system.ReleaseInstance()
        else:
            self._cam = cam_list[params['interface']['index']]
            self.cam.Init()
            # buffer mode https://www.flir.com/support-center/iis/machine-vision/application-note/understanding-buffer-handling/
            # Oldest first           - 0
            # Oldest First Overwrite - 1
            # Newest First           - 2
            # Newest First Overwrite - 3
            # Newest Only            - 4
            self.cam.TLStream.StreamBufferHandlingMode.SetValue(4)

            if self.cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
                self.logger.error('Unable to set acquisition mode to continuous', extra=self.log_args)
            else:
                self.reset_trigger()
                self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
                self.cam.BeginAcquisition()

            self.acquire_image()
            cam_list.Clear()

    def __del__(self):
        """
        De-initialize camera
        """
        self.release()

    def release(self):
        if self.cam is not None:
            self.cam.EndAcquisition()
            self.cam.DeInit()
        CameraCommunicable.release(self)

        if self._cam is not None:
            del self._cam

    def configure_trigger(self, trigger):
        """
        This function configures the camera to use a given trigger

        :param trigger: trigger for camera.
        :type  trigger: str
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        import PySpin

        triggers = {
            'line0': PySpin.TriggerSource_Line0,
            'line1': PySpin.TriggerSource_Line1,
            'line2': PySpin.TriggerSource_Line2,
            'line3': PySpin.TriggerSource_Line3,
            'software': PySpin.TriggerSource_Software
        }

        try:
            # Ensure trigger mode off
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                self.logger.warning('Unable to disable trigger mode', extra=self.log_args)
            # Ensure trigger source can be changed
            elif self.cam.TriggerSource.GetAccessMode() != PySpin.RW:
                self.logger.warning('Unable to get trigger source', extra=self.log_args)
            # Ensure trigger source is supported
            elif trigger not in triggers:
                self.logger.warning('Not supported trigger source: "{}"'.format(trigger), extra=self.log_args)
            # Set the trigger
            else:
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
                self.cam.TriggerSource.SetValue(triggers[trigger])
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
                return True

        except PySpin.SpinnakerException as ex:
            self.logger.warning('Error occurred during trigger configuration: {}'.format(str(ex)), extra=self.log_args)

        return False

    def configure_exposure(self, exposure_time):
        """
        This function configures a custom exposure time. Automatic exposure is turned
        off in order to allow for the customization, and then the custom setting is
        applied.

        :param exposure_time: exposure time value [ms], 0 for continues
        :type  exposure_time: float
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        import PySpin

        try:
            result = True

            # Try to disabe automatic exposure mode
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False

            if not exposure_time:
                self.cam.ExposureAuto.SetValue(True)
                return True
            else:
                self.cam.ExposureAuto.SetValue(False)

            # check if it possible to write exposure time
            if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False

            # Ensure desired exposure time does not exceed the maximum
            exposure_time = int(exposure_time * 1000)
            exposure_time = min(self.cam.ExposureTime.GetMax(), exposure_time)
            exposure_time = max(self.cam.ExposureTime.GetMin(), exposure_time)
            self.cam.ExposureTime.SetValue(exposure_time)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
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
        import PySpin

        try:
            result = True

            # Try to disabe automatic gain mode
            if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic gain. Aborting...')
                return False

            self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)

            # check if it possible to set gain
            if self.cam.Gain.GetAccessMode() != PySpin.RW:
                print('Unable to set gain. Aborting...')
                return False

            # Ensure desired gain does not exceed the maximum
            gain = min(self.cam.Gain.GetMax(), gain)
            self.cam.Gain.SetValue(gain)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
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
        import PySpin

        try:
            result = True

            # set gamma enable according to set value
            if self.cam.GammaEnable.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic gamma. Aborting...')
                return False

            if gamma is False:
                self.cam.GammaEnable.SetValue(False)
                return True
            else:
                self.cam.GammaEnable.SetValue(True)

            # check if it possible to set gamma
            if self.cam.Gamma.GetAccessMode() != PySpin.RW:
                print('Unable to set gamma. Aborting...')
                return False

            # Ensure desired gamma does not exceed the maximum
            gamma = min(self.cam.Gamma.GetMax(), gamma)
            self.cam.Gamma.SetValue(gamma)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def configure_saturation(self, saturation):
        """
        This function configures a custom saturation.

        :param saturation: saturation value, False set saturation to off
        :type  saturation float
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        import PySpin

        try:
            result = True

            # set saturation enable according to set value
            if self.cam.SaturationEnable.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic saturation. Aborting...')
                return False

            if self.cam.IspEnable.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic saturation. Aborting...')
                return False
            self.cam.IspEnable.SetValue(True)

            if saturation is False:
                self.cam.SaturationEnable.SetValue(False)
                return True
            else:
                self.cam.SaturationEnable.SetValue(True)

            # check if it possible to set saturation
            if self.cam.Saturation.GetAccessMode() != PySpin.RW:
                print('Unable to set saturation. Aborting...')
                return False

            # Ensure desired saturation does not exceed the maximum
            saturation = min(self.cam.Saturation.GetMax(), saturation)
            self.cam.Saturation.SetValue(saturation)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
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
        import PySpin

        try:
            result = True

            # Try to enable manual set of framerate
            if self.cam.AcquisitionFrameRate.GetAccessMode() != PySpin.RW:
                print('Unable to enable manual set of framerate. Aborting...')
                return False

            self.cam.AcquisitionFrameRateEnable.SetValue(True)

            # check if it possible to set framerate
            if self.cam.AcquisitionFrameRate.GetAccessMode() != PySpin.RW:
                print('Unable to set framerate time. Aborting...')
                return False

            # Ensure desired framerate does not exceed the maximum
            framerate = min(self.cam.AcquisitionFrameRate.GetMax(), framerate)
            self.cam.AcquisitionFrameRate.SetValue(framerate)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def configure_white_auto_balance(self, auto, damping=0.5, autolowerlimit=0.25, autoupperlimit=4):
        """
        This function set white balance

        :param auto: type of white autobalance (off, once, on)
        :type  auto: string
        :param damping: damping white balace change
        :type  damping: float
        :param autolowerlimit: lower change limit
        :type  autolowerlimit: float
        :param autoupperlimit: upper change limit
        :type  autoupperlimit: float
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        import PySpin

        try:
            result = True

            # Try to enable manual set of BalanceWhiteAuto
            if self.cam.BalanceWhiteAuto.GetAccessMode() != PySpin.RW:
                print('Unable to enable manual set of BalanceWhiteAuto. Aborting...')
                return False

            if auto == 'once':
                self.cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Once)
            elif auto == 'on':
                self.cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Continuous)
                self.cam.BalanceWhiteAutoDamping.SetValue(damping)
            else:
                self.cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Off)
                return True

            self.cam.BalanceWhiteAutoLowerLimit.SetValue(autolowerlimit)
            self.cam.BalanceWhiteAutoUpperLimit.SetValue(autoupperlimit)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def configure_sharpening(self, sharpening, automatic=False, threshold=0.1):
        """
        This function configure a custom sharpening.

        :param sharpening: saturation value, False set saturation to off
        :type  sharpening: float
        :param automatic: set automatic sharpening
        :type  automatic: bool
        :param threshold: Controls the minimum intensity gradient change to invoke sharpening
            High sharpen areas with hight intensity changes. Low thresholds sharpen more areas.
        :type  threshold: float (0 - 0.25)
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        import PySpin

        try:
            result = True

            # set sharpening enable according to set value
            if self.cam.SharpeningEnable.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic sharpening. Aborting...')
                return False

            if sharpening is False:
                self.cam.SharpeningEnable.SetValue(False)
                return True
            else:
                self.cam.SharpeningEnable.SetValue(True)

            # check if it possible to set sharpening
            if self.cam.Sharpening.GetAccessMode() != PySpin.RW:
                print('Unable to set sharpening. Aborting...')
                return False

            # Ensure desired saturation does not exceed the maximum
            sharpening = min(self.cam.Sharpening.GetMax(), sharpening)
            self.cam.Sharpening.SetValue(sharpening)
            if automatic:
                self.cam.SharpeningAuto.SetValue(True)
            else:
                self.cam.SharpeningAuto.SetValue(False)
                threshold = min(self.cam.SharpeningThreshold.GetMax(), threshold)
                threshold = max(self.cam.SharpeningThreshold.GetMin(), threshold)
                self.cam.SharpeningThreshold.SetValue(threshold)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def acquire_image(self):
        """
        acquire actual image from camera

        :returns: acquired image
        :rtype: cv2 image (b,g,r matrix)
        """
        import PySpin

        data = None

        try:
            # Set acquisition mode to continuous
            image_result = self.cam.GetNextImage()

            #  Ensure image completion
            if image_result.IsIncomplete():
                self.logger.warning('Image incomplete with image status: {}'.format(image_result.GetImageStatus()), extra=self.log_args)
            else:
                # Convert the Image object to BGR array
                image_converted = image_result.Convert(PySpin.PixelFormat_BGR8)
                self.img_width = image_result.GetWidth()
                self.img_height = image_result.GetHeight()
                data = image_converted.GetData()
                data = data.reshape(self.img_height, self.img_width, 3)

        except PySpin.SpinnakerException as ex:
            self.logger.error('Error occurred during image acquisition: {}'.format(str(ex)))

        return data

    def reset_trigger(self):
        """
        This function returns the camera to a normal state by turning off trigger mode.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """
        import PySpin

        try:
            # The trigger must be disabled in order to configure whether the source is software or hardware.
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                self.logger.warning('Unable to disable trigger mode', extra=self.log_args)
            else:
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
                return True

        except PySpin.SpinnakerException as ex:
            self.logger.warning('Error occurred during trigger reset: {}'.format(str(ex)))

        return False

    def get_info(self):
        """
        This function prints the device information of the camera from the transport
        layer; please see NodeMapInfo example for more in-depth comments on printing
        device information from the nodemap.

        :param nodemap: Transport layer device nodemap.
        :type  nodemap: INodeMap
        :returns: info in str
        :rtype: bool
        """
        import PySpin
        info = ''

        try:
            nodemap = self.cam.GetTLDeviceNodeMap()
            node_device_info = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

            if PySpin.IsAvailable(node_device_info) and PySpin.IsReadable(node_device_info):
                features = node_device_info.GetFeatures()

                for feature in features:
                    node_feature = PySpin.CValuePtr(feature)
                    node_value = node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'
                    info += '{}: {}\n'.format(node_feature.GetName(), node_value)
            else:
                info = 'Device control information not available'

        except PySpin.SpinnakerException as ex:
            self.logger.error('Error occurred during camera info retrieving: {}'.format(str(ex)))

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

    # def default_saturation(self, value):
    #     if not isinstance(value, float) and not isinstance (value, int) and not isinstance(value, bool):
    #         self.logger.error('Saturation value must be a float or bool', extra=self.log_args)
    #         return False
    #     return self.configure_saturation(value)

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

    # def default_sharpening(self, value):
    #     if not isinstance(value, bool):
    #         self.logger.error('Sharpening value must be a bool', extra=self.log_args)
    #         return False
    #     return self.configure_sharpening(value)

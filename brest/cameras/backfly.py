# -*- coding: utf-8 -*-
"""
    brest.cameras.backfly
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements Backfly camera.

    :copyright: 2019 Bender Robotics
"""

import logging

from brest.cameras import Cameras
from brest.communication import CameraCommunicable


class Backfly(Cameras, CameraCommunicable):
    """
    Backfly cameras

    :param params: Construction parameters
    :type  params: dict
    """

    Cameras.KNOWN['Backfly'] = {
        'type': 'camera',
        'service': 'PGRUSBCam3',
        }

    def __init__(self, params, trigger=None):
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

            if trigger is not None:
                self.configure_trigger(trigger)

            self.acquire_image()
            self.mark_taken(self)
            cam_list.Clear()

    def __del__(self):
        """
        De-initialize camera
        """
        if self.cam is not None:
            self.cam.DeInit()
        self.unmark_taken(self)

    def configure_trigger(self, trigger):
        """
        This function configures the camera to use a given trigger

        :param cam: Camera to configure trigger for.
        :type  cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        import PySpin

        TRIGGERS = {
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
            elif trigger not in TRIGGERS:
                self.logger.warning('Not supported trigger source: "{}"'.format(trigger), extra=self.log_args)
            # Set the trigger
            else:
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
                self.cam.TriggerSource.SetValue(TRIGGERS[trigger])
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
                return True

        except PySpin.SpinnakerException as ex:
            self.logger.warning('Error occurred during trigger configuration: {}'.format(str(ex)), extra=self.log_args)

        return False

    def acquire_image(self):
        import PySpin

        data = None

        try:
            # Set acquisition mode to continuous
            if self.cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
                self.logger.error('Unable to set acquisition mode to continuous', extra=self.log_args)
            else:
                self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
                self.cam.BeginAcquisition()
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

                self.cam.EndAcquisition()

        except PySpin.SpinnakerException as ex:
            self.logger.error('Error occurred during image acquisition: {}'.format(str(ex)))

        return data

    def reset_trigger(self):
        """
        This function returns the camera to a normal state by turning off trigger mode.

        :param cam: Camera to acquire images from.
        :type  cam: CameraPtr
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

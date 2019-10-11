import logging

from brest.cameras import Cameras
from brest.communication import CameraCommunicable

class Backfly(Cameras, CameraCommunicable):

    Cameras.KNOWN['Backfly'] = {
        'type': 'camera',
        'lib': 'PySpin'
        }

    def __init__(self, params, triger = None):
        Cameras.__init__(self, params)
        CameraCommunicable.__init__(self, params['interface'])

        try:
            import cv2
        except ModuleNotFoundError:
            raise ModuleNotFoundError('To use {} class you have to install `opencv-python` module'.format(self.__class__.__name__))
        try:
            import PySpin
        except ModuleNotFoundError:
            raise ModuleNotFoundError('To use {} class you have to install `PySpin` module'.format(self.__class__.__name__))
        try:
            import tempfile
        except ModuleNotFoundError:
            raise ModuleNotFoundError('To use {} class you have to install `tempfile` module'.format(self.__class__.__name__))

        # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()

        # Retrieve list of cameras from the system
        cam_list = self.system.GetCameras()

        num_cameras = cam_list.GetSize()

        # Finish if there are no cameras
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()

            # Release system instance
            self.system.ReleaseInstance()

            self.logger.error('No cameras connected', extra=self.log_args)
            raise SystemExit

        # Run example on each camera
        self._cam = cam_list[params['interface']['index']] # volba kamery
        cam_list.Clear()
        self.__inittrg(triger)
        self.acquire_image()
        self.mark_taken(self)

    def __del__(self):
        # Deinitialize camera
        if self.cam is not None:
            self.cam.DeInit()
        self.unmark_taken(self)

    def configure_trigger(self,triger):
        """
        This function configures the camera to use a trigger. First, trigger mode is
        ensured to be off in order to select the trigger source. Trigger mode is
        then enabled, which has the camera capture only a single image upon the
        execution of the chosen trigger.

        :param cam: Camera to configure trigger for.
        :type cam: CameraPtr
        :return: True if successful, False otherwise.
        :rtype: bool
        """

        import PySpin

        try:
            result = True

            # Ensure trigger mode off
            # The trigger must be disabled in order to configure whether the source
            # is software or hardware.
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                self.logger.warning('Unable to disable trigger mode', extra=self.log_args)
                return False

            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

            # Select trigger source
            # The trigger source must be set to hardware or software while trigger
            # mode is off.
            if self.cam.TriggerSource.GetAccessMode() != PySpin.RW:
                self.logger.warning('Unable to get trigger source', extra=self.log_args)
                return False
            if triger == ('line3'):
                self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line3)
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            elif triger == ('line2'):
                cam.TriggerSource.SetValue(PySpin.TriggerSource_Line2)
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            elif triger == ('line1'):
                cam.TriggerSource.SetValue(PySpin.TriggerSource_Line1)
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            elif triger == ('line0'):
                cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            elif triger == ('software'):
                cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)


            # Turn trigger mode on
            # Once the appropriate trigger source has been set, turn trigger mode
            # on in order to retrieve images using the trigger.



        except PySpin.SpinnakerException as ex:
            self.logger.warning('Error occured during trigger configuration: {}'.format(str(ex)), extra=self.log_args)
            return False

        return result

    def acquire_image(self):

        import cv2
        import PySpin
        import tempfile

        try:
            # Set acquisition mode to continuous
            if self.cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
                self.logger.error('Unable to set acquisition mode to continuous', extra=self.log_args)
                raise SystemExit

            self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

            #  Begin acquiring images
            self.cam.BeginAcquisition()

            # Retrieve, convert, and save images

                #  Retrieve next received image
            image_result = self.cam.GetNextImage()
            filename = ('Trigger-%d.jpg' % 1)
            temp = tempfile.NamedTemporaryFile(suffix='.jpg').name
            image_result.Save(temp)
            img = cv2.imread(temp)
            #  Ensure image completion
            if image_result.IsIncomplete():
                self.logger.warning('Image incomplete with image status: {}'.format(image_result.GetImageStatus()), extra=self.log_args)

            # End acquisition
            self.cam.EndAcquisition()

        except PySpin.SpinnakerException as ex:
            self.logger.error('Error occured during image acquisition: {}'.format(str(ex)))
            raise SystemExit

        return img

    def acquire_images(self, num_images = 1):
        frames = []

        for _ in range(num_images):
            frames.append(self.acquire_image())

        return frames

    def reset_trigger(self):
        """
        This function returns the camera to a normal state by turning off trigger mode.

        :param cam: Camera to acquire images from.
        :type cam: CameraPtr
        :returns: True if successful, False otherwise.
        :rtype: bool
        """

        import PySpin

        try:
            result = True
            # Ensure trigger mode off
            # The trigger must be disabled in order to configure whether the source
            # is software or hardware.
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                self.logger.warning('Unable to disable trigger mode', extra=self.log_args)
                return False

            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

        except PySpin.SpinnakerException as ex:
            self.logger.warning('Error occured during trigger reset: {}'.format(str(ex)))
            return False

        return result


    def get_info(self):
        """
        This function prints the device information of the camera from the transport
        layer; please see NodeMapInfo example for more in-depth comments on printing
        device information from the nodemap.

        :param nodemap: Transport layer device nodemap.
        :type nodemap: INodeMap
        :returns: info in str
        :rtype: bool
        """

        import PySpin

        nodemap= self.cam.GetTLDeviceNodeMap()

        try:
            result = True
            node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

            if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
                features = node_device_information.GetFeatures()
                info = ''
                for feature in features:
                    node_feature = PySpin.CValuePtr(feature)
                    info += ('%s: %s\n' % (node_feature.GetName(),
                                      node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))
                return info

            else:
                return ('Device control information not available')

        except PySpin.SpinnakerException as ex:
            self.logger.error('Error occured during camera info retrieving: {}'.format(str(ex)))
            raise SystemExit

    def detect_model(self):
        pass

    def __inittrg(self, triger):
        try:
            err = False

            # Initialize camera
            self.cam.Init()

            # Retrieve GenICam nodemap
            nodemap = self.cam.GetNodeMap()

            # Configure trigger
            self.configure_trigger(triger)

        except PySpin.SpinnakerException as ex:
            self.logger.error('Error occured during camera and trigger initialization: {}'.format(str(ex)))
            raise SystemExit

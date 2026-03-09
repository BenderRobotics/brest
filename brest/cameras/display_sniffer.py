#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.cameras.display_sniffer
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements "Display Sniffer" camera.

    :copyright: 2024 Bender Robotics
"""
import logging

from brest.cameras import Cameras
from brest.communication import DisplaySnifferCommunicable


class DisplaySniffer(Cameras, DisplaySnifferCommunicable):
    """
    Display Sniffer.

    Derived from: :class:`~brest.cameras.Cameras`, :class:`~brest.communication.DisplaySnifferCommunicable`

    :param params: Construction parameters
    :type  params: dict

    Implicit interface definition::

        interface:
            type:             'display_sniffer'
            timeout:          10.0
            serial_number:    None

    Note: It is recommended to use serial_number when targeting specific instance.
    """

    Cameras.KNOWN["DisplaySniffer"] = {
        "type": "display_sniffer",
        "service": "sniffer_usb",
        "serial_number": None,
        "init_timeout": 10.0,
    }

    def __init__(self, params):
        Cameras.__init__(self, params)
        DisplaySnifferCommunicable.__init__(self, params["interface"])
        try:
            from display_sniffer import DisplaySniffer as disniff
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "To use {} class you have to install `cameras_win` or `cameras_unix` module".format(
                    self.__class__.__name__
                )
            )

        self.timeout = 0.0
        self._cam = disniff()
        self._cam.open(timeout=params["interface"]["init_timeout"])

    def acquire_image(self):
        # If no timeout is set, set the timeout used in the Display Sniffer API
        raw = self._cam.grab_frame(self.timeout)
        return raw

    def get_info(self):
        """
        Fetches settings. Gets the dictionary of all settings.

        :returns: Dictionary of all settings, or None if error occurs.
        """
        info_dict = {
            "porch": self._cam.porch,
            "rotation": self._cam.rotation,
            "allow_delta_frames": self._cam.delta_frames,
            "timeout": self.timeout,
            "lvds_vesa": self._cam.lvds_vesa,
        }
        return info_dict

    def release(self):
        """
        Releases the camera
        Always close the device when your work is done.
        """
        Cameras.release(self)
        DisplaySnifferCommunicable.release(self)

        if self._cam is not None:
            self._cam.close()
            # Delete to ensure memory clearance and recreate variable for further functionality
            del self._cam
            self._cam = None

    def detect_model(self):
        """ """
        pass

    def default_timeout(self, value):
        """
        Setter of the timeout

        :param value: timeout
        :type value: float or int
        :rtype: bool
        """
        if not isinstance(value, (int, float)):
            self.logger.error(
                "Timeout value must be numeric ", extra=self.log_args
            )
            self.timeout = 0.0
            return False

        self.timeout = value
        return True

    def default_allow_delta_frames(self, value):
        """
        Setter of the allow delta frames default value

        :param value: allow delta frames
        :type value: bool
        :rtype: bool
        """
        if not isinstance(value, bool):
            self.logger.error(
                "`allow_delta_frames` value must be boolean ", extra=self.log_args
            )
            return False
        self._cam.delta_frames = value
        return True

    def default_rotation(self, value):
        """
        Setter of the rotation default value

        :param value: rotation
        :type value: int
        :rtype: bool
        """
        if not isinstance(value, int):
            self.logger.error("`rotation` value must be an integer ", extra=self.log_args)
            return False
        if 360 >= value >= 0 != value % 90:
            self.logger.error(
                "`rotation` value must be an increment of 90° (0, 90, 180, 270)",
                extra=self.log_args,
            )
            return False

        self._cam.rotation = value
        return True

    def default_left_porch(self, value):
        """
        Setter of the left porch default value

        :param value: left porch
        :type value: int
        :rtype: bool
        """
        if not isinstance(value, int) and value < 0:
            self.logger.error(
                "`left_porch` value must be an integer and bigger than or equal 0 ",
                extra=self.log_args,
            )
            return False

        list_vals = list(self._cam.porch)
        list_vals[0] = value
        self._cam.porch = tuple(list_vals)
        return True

    def default_top_porch(self, value):
        """
        Setter of the top porch default value

        :param value: top porch
        :type value: int
        :rtype: bool
        """
        if not isinstance(value, int) and value < 0:
            self.logger.error(
                "`top_porch` value must be an integer and bigger than or equal 0 ",
                extra=self.log_args,
            )
            return False

        list_vals = list(self._cam.porch)
        list_vals[1] = value
        self._cam.porch = tuple(list_vals)
        return True

    def default_right_porch(self, value):
        """
        Setter of the right porch default value

        :param value: right porch
        :type value: int
        :rtype: bool
        """
        if not isinstance(value, int) and value < 0:
            self.logger.error(
                "`right_porch` value must be an integer and bigger than or equal 0 ",
                extra=self.log_args,
            )
            return False

        list_vals = list(self._cam.porch)
        list_vals[2] = value
        self._cam.porch = tuple(list_vals)
        return True

    def default_bottom_porch(self, value):
        """
        Setter of the bottom porch default value

        :param value: bottom porch
        :type value: int
        :rtype: bool
        """
        if not isinstance(value, int) and value < 0:
            self.logger.error(
                "`bottom_porch` value must be an integer and bigger than or equal 0 ",
                extra=self.log_args,
            )
            return False

        list_vals = list(self._cam.porch)
        list_vals[3] = value
        self._cam.porch = tuple(list_vals)
        return True

    def default_lvds_vesa(self, value):
        """
        Setter of the lvds_vesa default value

        :param value: lvds_vesa
        :type value: bool
        :rtype: bool
        """
        if not isinstance(value, bool):
            self.logger.error(
                "`lvds_vesa` value must be boolean ", extra=self.log_args
            )
            return False

        self._cam.lvds_vesa = value
        return True

    def _preprocess(self, img_raw):
        return img_raw

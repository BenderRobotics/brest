#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.cameras.cameras
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements base abstract class for cameras.

    :copyright: 2021 Bender Robotics
"""

import time
import logging
from threading import Event, Thread
from datetime import datetime
from typing import Optional, Tuple, Callable, Union

from brest import Resource


class Cameras(Resource):
    """
    Base abstract class for representing a camera.
    """

    KNOWN = {}
    VIDEO_TEXT_PLACEHOLDER_TIMESTAMP = '{timestamp}'

    def __init__(self, params=None):
        Resource.__init__(self, params)
        self._cam = None
        self._stop_event = None
        self._video_thread = None
        self.img_width = 0
        self.img_height = 0
        self.dstmaps = None
        self.transformation = None
        self.final_resolution = None
        self.hist_calibration = None
        self.ccm = None

        self._default_video_filename = None
        self._default_video_format = 'mp4'
        self._default_video_codec = 'libx264'
        self._default_video_fps = 20
        self._default_video_width = None
        self._default_video_text_color = (255, 255, 255)
        self._default_video_text = None

    @property
    def cam(self):
        """
        Camera interface reference.
        """

        return self._cam

    @property
    def resolution(self):
        """
        Camera image resolution in pixels (width, height).
        """

        return (self.img_width, self.img_height)

    @property
    def rectification_calibrated(self):
        """
        Returns True when rectification calibration is done for this camera and camera can give rectified image.
        """

        return (self.dstmaps is not None) and (self.transformation is not None) and (self.final_resolution is not None)

    @property
    def histogram_calibrated(self):
        """
        Returns True when rectification calibration is done for this camera and camera can give histogram-adjusted image.
        """

        return (self.hist_calibration is not None)

    @property
    def colors_calibrated(self):
        """
        Returns True when color calibration is done for this camera and camera can give color-calibrated image.
        """

        return (self.ccm is not None)

    def release(self):
        """
        Releases the camera resource.
        """
        self.stop_video_record()

    def acquire_image(self):
        """
        Acquire an image from the camara.
        """

        raise NotImplementedError('This camera has no meas of image acquisition')

    def acquire_images(self, num_images=1, period=0):
        """
        Acquire a returns one or more images in a list.

        :param num_images: number of images to acquire
        :type  num_images: int
        :param period: delay in between acquisition of two images in [s]
        :type period: float
        :return: list of images
        """

        frames = []

        for _ in range(int(num_images)):
            tic = time.time()
            frames.append(self.acquire_image())

            if period > 0:
                pause = max(0, period - (time.time() - tic))
                time.sleep(pause)

        return frames

    def reset_trigger(self):
        """
        Turn off camera trigger.
        """

        raise NotImplementedError('This camera doesn\'t support trigger')

    def get_info(self):
        """
        Returns info string.
        """

        raise NotImplementedError('This camera has no means of info detection.')

    def detect_model(self):
        """
        Returns model info. Implicitly tries to apply model's limits and specifications.
        """

        raise NotImplementedError('This supply does not support specific model detection.')

    def rectify(self, img):
        """
        Applies distortion correction and perspective transformation and returns image
        with desired resolution. Use get_transformation() to get necessary parameters.

        :param img: acquired image
        :type  img: cv2 image (b,g,r matrix)
        :return: undistorted and cropped image
        :rtype: cv2 image (b,g,r matrix)
        """
        import cv2 as cv

        assert self.dstmaps is not None, "Un-distortion maps are required, use `calibrate_shape` method."
        assert self.transformation is not None, "Transformation matrix are required, use `calibrate_shape` method."
        assert self.final_resolution is not None, "Final resolution is required, use `calibrate_shape` method."

        img_remaped = cv.remap(img, self.dstmaps[0], self.dstmaps[1], cv.INTER_LINEAR)
        img_final = cv.warpPerspective(img_remaped, self.transformation, self.final_resolution)
        return img_final

    def calibrate_hist(self, img):
        """
        Histogram calibration on acquired image

        :param img: acquired image
        :type  img: cv2 image (b,g,r matrix)
         :return: histogram calibrated image
        :rtype: cv2 image (b,g,r matrix)
        """
        import numpy as np

        imgo = img.copy()
        for x in range(0, 3):
            img_color = img[:, :, x]
            p = self.hist_calibration[x]
            # set mean value of color from chessboar image (black/white image) to center of histogram
            # (format init16 for possible calculation out of space uinit8)
            lower_change = np.array(img_color * (127/p[1]))
            upper_change = np.array((img_color-p[1]) * (127 / (255-p[1])) + 127)
            k = np.where(img_color < p[1], lower_change, upper_change).astype('int16')
            # stretching the histogram
            imgo[:, :, x] = np.clip((k-p[0]) * (255 / (p[2]-p[0])), 0, 255).astype('uint8')
        return imgo

    def apply_color_correction(self, img):
        """
        Applies color calibration matrix calculated in `calibrate_color` on acquired image.

        WARNING: original instance of `img` is affected by this function.

        :param img: acquired image
        :type  img: cv2 image (b,g,r matrix)
        :return: RGB color calibrated image
        :rtype: cv2 image (b,g,r matrix)
        """
        import numpy as np

        # reshape the source image to 1 channel, width * height rows, 3 cols,
        # apply color correction matrix and reshape back
        h, w, ch = img.shape
        img = np.reshape(img, (h * w, ch))
        img = img.dot(self.ccm)
        img = np.reshape(img, (h, w, ch))
        img = np.uint8(np.clip(img, 0, 255))
        return img

    @staticmethod
    def img_to_grayscale(img):
        """
        Converts image to gray-scale.

        :param img: cv image
        :return: image converted to grayscale
        """
        import cv2 as cv

        if len(img.shape) == 3 and img.shape[2] == 3:
            return cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        else:
            return img

    def calibrate_shape(self, img, scale, chessboard_size, display_size, border):
        """
        Does the calibration on the calibration images, calculates rectification parameters
        rom captured chessboard calibration image.

        :param img: image of the chessboard pattern
        :param float scale: scale between camera resolution and real display
        :param chessboard_size: number of black/white pairs
        :type  chessboard_size: int/float (width, height)
        :param display_size: resolution of display in px
        :type  tuple display_size: int (width, height)
        :param int border: border (in pixels) around cropped display
        """
        import numpy as np
        import cv2 as cv

        # termination criteria - epsilon reached and number of iterations
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # size of chessboard (from white/black pairs to rows and cols) and image
        w_ch, h_ch = int(chessboard_size[0]*2 - 3), int(chessboard_size[1]*2 - 3)
        # image size (columns, rows)
        size = (img.shape[1], img.shape[0])
        # prepare object points
        object_points = np.zeros((w_ch*h_ch, 3), np.float32)
        object_points[:, :2] = np.mgrid[0:h_ch, 0:w_ch].T.reshape(-1, 2)

        # find the chessboard corners
        img_gray = self.img_to_grayscale(img)
        ret, corners = cv.findChessboardCorners(img_gray, (h_ch, w_ch), None)

        # raise exception and terminate if chessboard is not found in the image
        if not ret:
            raise Exception("Image of chessboard [{}x{}] not found in the image.".format(w_ch, h_ch))

        # find corners with higher precision
        corners_sub = cv.cornerSubPix(img_gray, corners, (11, 11), (-1, -1), criteria)

        # - Find intrinsic and extrinsic parameters from view of a calibration pattern,
        # - get new camera matrix based on found parameters,
        # - computes the un-distortion and rectification transformation map,
        # - and apply a geometrical transformation to an image.
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv.calibrateCamera([object_points], [corners_sub], size, None, None)
        new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, size, 1, size)
        dstmaps = cv.initUndistortRectifyMap(camera_matrix, dist_coeffs, None, new_camera_matrix, size, cv.CV_32FC1)
        img_remaped = cv.remap(img, dstmaps[0], dstmaps[1], cv.INTER_LINEAR)
        img_gray = self.img_to_grayscale(img_remaped)

        # find the chessboard corners in the transformed image
        ret, corners = cv.findChessboardCorners(img_gray, (h_ch, w_ch), None)
        corners_sub = cv.cornerSubPix(img_gray, corners, (3, 3), (-1, -1), criteria)
        final_resolution = (int(display_size[0]*scale + border*2),
                            int(display_size[1]*scale + border*2))
        # corner points found in the chessboard image
        source_points = np.float32([corners_sub[-1, 0],
                                    corners_sub[h_ch-1, 0],
                                    corners_sub[-h_ch, 0],
                                    corners_sub[0, 0]])
        # expected coordinations of the chessboard corners
        ch_b = display_size[0] * scale / chessboard_size[0] + border
        dest_points = np.float32([[ch_b, final_resolution[1]-ch_b],
                                  [final_resolution[0]-ch_b, final_resolution[1]-ch_b],
                                  [ch_b, ch_b],
                                  [final_resolution[0]-ch_b, ch_b]])
        transformation = cv.getPerspectiveTransform(source_points, dest_points)

        self.dstmaps = dstmaps
        self.transformation = transformation
        self.final_resolution = final_resolution

    def calibrate_color(self, colors, images):
        """
        Calculates color-calibration matrix based on the images captured with the camera and the expected colors.

        :param colors: list of colours in tuple representation - same color order as the `images`, by default OpenCV is
                       using color channel order (B, G, R).
        :param images: list of images of the `colors`
        """
        import numpy as np
        import cv2 as cv

        assert len(colors) == len(images)
        n = len(colors)
        source = np.zeros((n, 3))
        target = np.zeros((n, 3))

        for i, img in enumerate(images):
            # crop image to the middle part
            h, w = img.shape[0], img.shape[1]
            x = int(w // 4)
            y = int(w // 4)
            h = int(h // 2)
            w = int(w // 2)
            crop_img = img[y:y+h, x:x+w]

            # get average color of the given image
            pixels = np.float32(crop_img.reshape(-1, 3))
            source[i] = np.average(pixels, axis=0)
            target[i] = colors[i]

        # compute the colour correction matrix: A*CCM = B => CCM = (A' * A).inv() * A' * B
        at_b = np.transpose(source).dot(target)
        at_a_inv = np.linalg.pinv(np.transpose(source).dot(source))
        self.ccm = at_a_inv.dot(at_b)

    def _preprocess(self, img_raw):
        """
        Executes rectification, color adjustment and crop to display are on the acquired image.

        :param img_raw: Input image from the camera
        :type  img_raw: image
        :return: pre-processed image
        :rtype: image
        """
        img = self.rectify(img_raw)

        if self.hist_calibration is not None:
            img = self.calibrate_hist(img)

        if self.ccm is not None:
            img = self.apply_color_correction(img)

        return img

    def acquire_calibrated_image(self):
        """
        Acquire image from the camera and does the preprocessing.

        :return: calibrated image
        :rtype: image
        """
        # Carpute image
        raw = self.acquire_image()
        return self._preprocess(raw)

    def acquire_calibrated_images(self, num_images, period):
        """
        Acquire image from the camera and does the preprocessing.

        :return: Sequence of calibrated images
        :rtype: Sequence of images
        """
        raws = self.acquire_images(num_images, period)
        return [self._preprocess(raw) for raw in raws]

    # Video support

    def default_video_filename(self, value):
        """
        Setter of the video_filename default value

        :param value: path to the filename
        :type value: str
        :rtype: bool
        """
        if not isinstance(value, str):
            self.logger.error('Video filename value must be a string', extra=self.log_args)
            return False

        self._default_video_filename = value
        return True

    def default_video_format(self, value):
        """
        Setter of the video_format default value

        :param value: video format
        :type value: str
        :rtype: bool
        """
        if not isinstance(value, str):
            self.logger.error('Video format value must be a string', extra=self.log_args)
            return False

        self._default_video_format = value
        return True

    def default_video_codec(self, value):
        """
        Setter of the video_codec default value

        :param value: video codec
        :type value: str
        :rtype: bool
        """
        if not isinstance(value, str):
            self.logger.error('Video codec value must be a string', extra=self.log_args)
            return False

        self._default_video_codec = value
        return True

    def default_video_fps(self, value):
        """
        Setter of the video_fps default value

        :param value: video FPS
        :type value: int
        :rtype: bool
        """
        try:
            value = int(value)
        except ValueError:
            self.logger.error('Video FPS value must be an integer', extra=self.log_args)
            return False
        else:
            if not value > 0:
                self.logger.error('Video FPS value must be an integer > 0', extra=self.log_args)
                return False

        self._default_video_fps = value
        return True

    def default_video_width(self, value):
        """
        Setter of the video_width default value

        :param value: video width
        :type value: int | None
        :rtype: bool
        """
        if value is not None:
            try:
                value = int(value)
            except ValueError:
                self.logger.error('Video width value must be an integer', extra=self.log_args)
                return False
            else:
                if not isinstance(value, int) or not value > 0:
                    self.logger.error('Video width value must be an integer > 0', extra=self.log_args)
                    return False
        else:
            # if None is given, we will use the camera resolution
            pass

        self._default_video_width = value
        return True

    def default_video_text_color(self, value):
        """
        Setter of the video_text_color default value

        :param value: video text color
        :type value: str | tuple[int, int, int]
        :rtype: bool
        """
        if isinstance(value, str):
            value = value.strip('#')

            if len(value) == 3:
                value = (int(value[2], 16), int(value[1], 16), int(value[0], 16))           # RGB to OpenCV BGR
            elif len(value) == 6:
                value = (int(value[4:6], 16), int(value[2:4], 16), int(value[0:2], 16))     # RGB to OpenCV BGR
            else:
                self.logger.error(f'Unsupported text color format {value} for video text color', extra=self.log_args)
                return False

        if isinstance(value, list):
            value = tuple(value)

        if not isinstance(value, tuple) or len(value) != 3:
            self.logger.error(f'Video text color value must be a tuple with 3 items, value `{value}` (type of {type(value)}) given', extra=self.log_args)
            return False

        self._default_video_text_color = value
        return True

    def default_video_text(self, value):
        """
        Setter of the video_text default value

        :param value: video text
        :type value: text
        :rtype: bool
        """
        if (value is not None) and not isinstance(value, str):
            self.logger.error('Video text value must be a string', extra=self.log_args)
            return False

        self._default_video_text = value
        return True

    def start_video_record(self,
                           filename: Optional[str] = None,
                           video_format: Optional[str] = None,
                           codec: Optional[str] = None,
                           fps: Optional[int] = None,
                           frame_width: Optional[int] = None,
                           text: Optional[str] = None,
                           text_color: Optional[Union[str, Tuple[int, int, int]]] = None) -> None:
        """
        Starts recording of the video created from the camera frames

        :param filename: name of the output video file,
                         extension .mov, .avi, .mpg, .mpeg, .mp4, .mkv, .wmv are supported
        :type filename: str
        :param video_format: video format
        :type video_format: str
        :param codec: video codec
        :type codec: str
        :param fps: number of frames per second
        :type fps: int
        :param frame_width: width of the video frame in pixels
        :type frame_width: int
        :param text: optional text to be put in the video frames, supports '{timestamp}' placeholder
        :type text: str
        :param text_color: color of the text to be put in the video frames
        :type text_color: tuple | str
        """
        filename = self._default_video_filename if filename is None else filename
        video_format = self._default_video_format if video_format is None else video_format
        codec = self._default_video_codec if codec is None else codec
        fps = self._default_video_fps if fps is None else fps
        frame_width = self._default_video_width if frame_width is None else frame_width
        text_color = self._default_video_text_color if text_color is None else text_color
        text = self._default_video_text if text is None else text

        # Change color string to tuple
        if isinstance(text_color, str):
            text_color = text_color.strip('#')

            if len(text_color) == 3:
                text_color = (int(text_color[2], 16), int(text_color[1], 16), int(text_color[0], 16))           # RGB to OpenCV BGR
            elif len(text_color) == 6:
                text_color = (int(text_color[4:6], 16), int(text_color[2:4], 16), int(text_color[0:2], 16))     # RGB to OpenCV BGR
            else:
                raise AssertionError(f'Unsupported text color format {text_color} for video text color')

        # Convert FPS if possible to int
        try:
            fps = int(fps)
        except ValueError:
            raise AssertionError(f'`fps` has to be an integer, {type(fps)} given ({fps}')

        assert filename, '`filename` has to be specified!'
        assert isinstance(video_format, str), '`video_format` has to be a string.'
        assert isinstance(codec, str), '`codec` has to be a string.'
        assert isinstance(fps, int) and fps > 0, '`fps` has to be an integer greater than zero.'
        assert (frame_width is None) or (isinstance(frame_width, int) and frame_width > 0), '`frame_width` has to be an integer greater than zero.'
        assert isinstance(text_color, tuple) and len(text_color) == 3, '`text_color` has to be a tuple with 3 items.'
        assert (text is None) or isinstance(text, str), '`text` has to be a string.'

        def _frame_grabber(frame_acquire_func: Callable, writer, period: float,
                           video_width: int, text: Optional[str], text_color, stop_event):
            '''This function runs in dedicated threads, reads the images from the camera and writes them to the output record.

            :param frame_acquire_func: function to be used to acquire the frames from the camera
            :type frame_acquire_func: callable
            :param writer: video writer
            :type writer: imageio.Writer
            :param period: time period in between two frames (1 / FPS)
            :type period: float
            :param video_width: horizontal resolution of the video in px
            :type video_width: int
            :param text: text to be added to each frame
            :type text: str
            :param text_color: color of the `text`
            :type text_color: tuple[int, int, int] | str
            :param stop_event: thread event pill to kill
            :type stop_event: threading.Event
            '''
            try:
                import cv2 as cv
                t = 0
                macro_block_size = 16   # codec usually uses block size of 16px, use the multiplication of 16 in resolution
                # take one frame to calculate output height
                frame = frame_acquire_func()
                (frame_width, frame_height) = (frame.shape[1], frame.shape[0])

                # check if there is a specified resolution of the video, if not use the camera resolution
                if video_width is not None:
                    video_width = int(round(video_width / macro_block_size) * macro_block_size)
                    video_height = (video_width / frame_width) * frame_height
                else:
                    video_width = int(round(frame_width / macro_block_size) * macro_block_size)
                    video_height = frame_height

                video_height = int(round(video_height / macro_block_size) * macro_block_size)

                # create thickness and scale of the font based on the image resolution, use scale 1 on resolution 1600
                font_scale = video_width / 2048
                text_line_height = int(30 * font_scale)

                # get the coordinates where to put the text
                text_x = int(10 * font_scale)
                text_y = text_x + text_line_height

                # loop with fixed period terminated by killing pill `stop_event`
                while not stop_event.wait(max(0, (t + period) - time.time())):
                    t = time.time()

                    # take a frame and resample it to the output resolution
                    frame = frame_acquire_func()
                    frame = cv.resize(frame, (video_width, video_height), interpolation=cv.INTER_AREA)

                    if text:
                        # add text line by line
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        row_y = text_y

                        for line in text.split(r'\n'):
                            line = line.replace(Cameras.VIDEO_TEXT_PLACEHOLDER_TIMESTAMP, timestamp)
                            frame = cv.putText(frame, line, (text_x, row_y), cv.FONT_HERSHEY_SIMPLEX, font_scale,
                                               text_color, lineType=cv.LINE_8)
                            row_y += text_line_height

                    # CV by default works in BGR -> change to RGB
                    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    writer.append_data(frame)

            except Exception as ex:
                log_args = {'class_name': '_frame_grabber'}
                logging.getLogger().error(ex, exc_info=ex, extra=log_args)

            finally:
                writer.close()

        try:
            import imageio
            import cv2 as cv
        except ModuleNotFoundError:
            raise ModuleNotFoundError('To use video recording you have to install `imageio` and `open-cv` modules')
        else:
            writer = imageio.get_writer(filename, format=video_format, mode='I', fps=fps, codec=codec)
            period = 1.0 / float(fps) if fps != 0 else 0.05
            self._stop_event = Event()
            self._stop_event.clear()
            self._video_thread = Thread(target=_frame_grabber, args=(self.acquire_image, writer, period,
                                                                     frame_width, text, text_color, self._stop_event))
            self._video_thread.daemon = True
            self._video_thread.start()

    def stop_video_record(self) -> None:
        """
        Stops video recording
        """
        if self._stop_event is not None:
            self._stop_event.set()

        if self._video_thread is not None:
            self._video_thread.join()

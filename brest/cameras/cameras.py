# -*- coding: utf-8 -*-
"""
    brest.helpers
    ~~~~~~~~~~~~~

    This module implements base abstract class for cameras.

    :copyright: 2019 Bender Robotics
"""

import time

from brest import Resource


class Cameras(Resource):
    """
    Base abstract class for representing a camera.
    """

    KNOWN = {}

    def __init__(self, params=None):
        Resource.__init__(self, params)
        self._cam = None
        self.img_width = 0
        self.img_height = 0
        self.dstmaps = None
        self.transformation = None
        self.final_resolution = None
        self.hist_calibration = None
        self.rgb_calibration = None

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

        return (self.rgb_calibration is not None)

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

    def calibrate_rgb(self, img):
        """
        RGB color calibration on acquired image

        :param img: acquired image
        :type  img: cv2 image (b,g,r matrix)
        :return: RGB color calibrated image
        :rtype: cv2 image (b,g,r matrix)
        """
        import numpy as np

        imgo = img.copy()
        bb = img[:, :, 0]
        bg = img[:, :, 1]
        br = img[:, :, 2]
        gb = img[:, :, 0]
        gg = img[:, :, 1]
        gr = img[:, :, 2]
        rb = img[:, :, 0]
        rg = img[:, :, 1]
        rr = img[:, :, 2]

        bo = bb * self.rgb_calibration[0, 0] + bg * self.rgb_calibration[1, 0] + br * self.rgb_calibration[2, 0]
        go = gb * self.rgb_calibration[0, 1] + gg * self.rgb_calibration[1, 1] + gr * self.rgb_calibration[2, 1]
        ro = rb * self.rgb_calibration[0, 2] + rg * self.rgb_calibration[1, 2] + rr * self.rgb_calibration[2, 2]

        imgo[:, :, 0] = np.clip(bo, 0, 255).astype('uint8')
        imgo[:, :, 1] = np.clip(go, 0, 255).astype('uint8')
        imgo[:, :, 2] = np.clip(ro, 0, 255).astype('uint8')

        return imgo

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

    def calibrate_color(self, chessboard, red, green, blue, chessboard_size):
        """
        Does the calibration on the calibration images.

        :param chessboard: image of the chessboard pattern
        :type  chessboard: image
        :param red: image of the red calibration screen
        :type  red: image
        :param green: image of the green calibration screen
        :type  green: image
        :param blue: image of the blue calibration screen
        :type  blue: image
        :param chessboard_size: number of black/white pairs
        :type  chessboard_size: int/float (width, height)
        """
        import numpy as np
        import cv2 as cv

        chessboard = self.rectify(chessboard)
        red = self.rectify(red)
        green = self.rectify(green)
        blue = self.rectify(blue)

        # BGR screen cropped to better function
        b = b[50:-50, 50:-50]
        g = g[50:-50, 50:-50]
        r = r[50:-50, 50:-50]

        hist_bins = 255
        hist_range = (0, 255)
        hist_threshold = 10

        crb, prb = np.histogram(np.ma.masked_less(r[:, :, 0], hist_threshold), bins=hist_bins, range=hist_range)
        crg, prg = np.histogram(np.ma.masked_less(r[:, :, 1], hist_threshold), bins=hist_bins, range=hist_range)
        crr, prr = np.histogram(np.ma.masked_less(r[:, :, 2], hist_threshold), bins=hist_bins, range=hist_range)
        cbb, pbb = np.histogram(np.ma.masked_less(b[:, :, 0], hist_threshold), bins=hist_bins, range=hist_range)
        cbg, pbg = np.histogram(np.ma.masked_less(b[:, :, 1], hist_threshold), bins=hist_bins, range=hist_range)
        cbr, pbr = np.histogram(np.ma.masked_less(b[:, :, 2], hist_threshold), bins=hist_bins, range=hist_range)
        cgb, pgb = np.histogram(np.ma.masked_less(g[:, :, 0], hist_threshold), bins=hist_bins, range=hist_range)
        cgg, pgg = np.histogram(np.ma.masked_less(g[:, :, 1], hist_threshold), bins=hist_bins, range=hist_range)
        cgr, pgr = np.histogram(np.ma.masked_less(g[:, :, 2], hist_threshold), bins=hist_bins, range=hist_range)
        cbb = np.where(0.95*max(cbb) < cbb, 0.95*max(cbb), cbb)
        cgg = np.where(0.95*max(cgg) < cgg, 0.95*max(cgg), cgg)
        crr = np.where(0.95*max(crr) < crr, 0.95*max(crr), crr)

        bmin = min(np.argmax(crb), np.argmax(cgb))
        gmin = min(np.argmax(crg), np.argmax(cbg))
        rmin = min(np.argmax(cbr), np.argmax(cbg))

        if cbb[-1] > 10:
            bmax = np.argmax(cbb)
        else:
            bmax = 255
        if cgg[-1] > 10:
            gmax = np.argmax(cgg)
        else:
            gmax = 255
        if crr[-1] > 10:
            rmax = np.argmax(crr)
        else:
            rmax = 255

        bmean = int(np.mean(chessboard_img[:, :, 0]))
        gmean = int(np.mean(chessboard_img[:, :, 1]))
        rmean = int(np.mean(chessboard_img[:, :, 2]))

        bp = [bmin, bmean, bmax]
        gp = [gmin, gmean, gmax]
        rp = [rmin, rmean, rmax]
        self.hist_calibration = [bp, gp, rp]

        b = self.calibrate_hist(b)
        g = self.calibrate_hist(g)
        r = self.calibrate_hist(r)
        chessboard_img = self.calibrate_hist(chessboard_img)

        Bi = [np.mean(b[:, :, 0]), np.mean(b[:, :, 1]), np.mean(b[:, :, 2])]
        Gi = [np.mean(g[:, :, 0]), np.mean(g[:, :, 1]), np.mean(g[:, :, 2])]
        Ri = [np.mean(r[:, :, 0]), np.mean(r[:, :, 1]), np.mean(r[:, :, 2])]

        chb = cv.GaussianBlur(chessboard_img, (9, 9), 10)
        chb = cv.GaussianBlur(chb, (5, 5), 20)
        h, w = chb.shape[:2]  # image size
        ws = int(w/chessboard_size[0])
        hs = int(h/chessboard_size[1])

        i = 0
        wb = 0
        wg = 0
        wr = 0
        kb = 0
        kg = 0
        kr = 0

        for x in range(int(chessboard_size[0])):
            for y in range(int(chessboard_size[1])):
                # calculation of center for white and black square in black/white pair
                x1 = int(ws*x + ws/4)
                x2 = int(ws*x + ws*3/4)
                y1 = int(hs*y + hs/4)
                y2 = int(hs*y + hs*3/4)

                wb += (int(chb[y1, x1, 2]) + int(chb[y2, x2, 2])) / 2
                wg += (int(chb[y1, x1, 2]) + int(chb[y2, x2, 2])) / 2
                wr += (int(chb[y1, x1, 2]) + int(chb[y2, x2, 2])) / 2
                kb += (int(chb[y1, x2, 0]) + int(chb[y2, x1, 0])) / 2
                kg += (int(chb[y1, x2, 1]) + int(chb[y2, x1, 1])) / 2
                kr += (int(chb[y1, x2, 2]) + int(chb[y2, x1, 2])) / 2
                i += 1

        Wi = [wb/(i-1), wg/(i-1), wr/(i-1)]
        Ki = [kb/(i-1), kg/(i-1), kr/(i-1)]
        I = [Bi, Gi, Ri, Wi, Ki, Wi, Ki, Wi, Ki]

        Bt = [255, 0, 0]
        Gt = [0, 255, 0]
        Rt = [0, 0, 255]
        Wt = [255, 255, 255]
        Kt = [0, 0, 0]
        T = [Bt, Gt, Rt, Wt, Kt, Wt, Kt, Wt, Kt]

        invI = np.linalg.pinv(I)

        self.rgb_calibration = np.dot(invI, T)

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

        if self.rgb_calibration is not None:
            img = self.calibrate_rgb(img)

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

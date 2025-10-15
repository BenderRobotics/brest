#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.tools.benchmark_cv_api
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This script tests image acquisition using all opencv backend apis to benchmark performance

    :copyright: 2024 Bender Robotics
"""
from copy import deepcopy
import os
import time
import brest
import cv2

curr_ver = brest.__version__
print(f'OpenCV API benchmark starting. Current brest version: {curr_ver}')

APIs = [
        'CAP_ANY',
        'CAP_VFW',
        'CAP_V4L',
        'CAP_V4L2',
        'CAP_FIREWIRE',
        'CAP_FIREWARE',
        'CAP_IEEE1394',
        'CAP_DC1394',
        'CAP_CMU1394',
        'CAP_QT',
        'CAP_UNICAP',
        'CAP_DSHOW',
        'CAP_PVAPI',
        'CAP_OPENNI',
        'CAP_OPENNI_ASUS',
        'CAP_ANDROID',
        'CAP_XIAPI',
        'CAP_AVFOUNDATION',
        'CAP_GIGANETIX',
        'CAP_MSMF',
        'CAP_WINRT',
        'CAP_INTELPERC',
        'CAP_OPENNI2',
        'CAP_OPENNI2_ASUS',
        'CAP_GPHOTO2',
        'CAP_GSTREAMER',
        'CAP_FFMPEG',
        'CAP_IMAGES',
        'CAP_ARAVIS',
        'CAP_OPENCV_MJPEG',
        'CAP_INTEL_MFX',
        'CAP_XINE',
]

results = []
cam_resource = {
    'class_name': 'cameras.GenericCamera',
    'interface': {
        'service': 'usbvideo',
        'cv_api': 'CAP_ANY',
        'index': 0
    }
}
backends = cv2.videoio_registry.getBackends()
backends = [0] + list(backends)  # Add 0 - CAP_ANY to the list
print(f'Supported backends: {backends}')

for api_name in APIs:
    print(f'\n====== Testing API: {api_name} ======')
    eval_str = 'cv2.' + api_name
    cv_api = eval(eval_str)

    result = {}
    result['api'] = api_name
    result['delta_init'] = None
    result['delta_img'] = None
    result['img'] = None

    if cv_api in backends:
        cam_res_local = deepcopy(cam_resource)

        delta = None
        rp = brest.ResourceProvider()
        cam_res_local['interface']['cv_api'] = api_name
        print(f'cam resource: {cam_res_local}')

        start = time.perf_counter()
        cam = rp.construct(params=cam_res_local)
        end = time.perf_counter()
        delta = end-start
        print(f'cam constructed in {delta}')
        result['delta_init'] = delta

        img = None
        try:
            start = time.perf_counter()
            img = cam.acquire_image()
            end = time.perf_counter()
            delta = end-start
            result['delta_img'] = delta
        except Exception as ex:
            print(f'Exception while acquiring image (api = {api_name}):\n{ex}')

        result['img'] = img
        results.append(result)

        cam.release()
        del(cam)
    else:
        results.append(result)
        print(f'API {api_name} ({cv_api}) does not match any of locally supported APIs {backends}')

print('\nRESULTS ==================================================================')

not_supported = []
for result in results:
    if result['img'] is None:
        not_supported.append(result['api'])
print(f'List of not supported APIs: {not_supported}')

print(f'\nSupported APIs:')
for result in results:
    if result['img'] is not None:
        print(f"API {result['api']} - delta init: {result['delta_init']:.05}, delta img: {result['delta_img']:.05}")
        # cv2.imshow(result['api'], result['img'])

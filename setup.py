#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.setup
    ~~~~~~~~~~~

    Setup file for package building.

    :copyright: 2021 Bender Robotics
"""

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='brest',
    version='0.0.14',
    author='Bender Robotics',
    author_email='lesinsky@benderrobotics.com',
    description='Bender Robotics Embedded Systems Toolkit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.benderrobotics.com',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5, <3.10',
    entry_points={
          'console_scripts': [
              'brest.gui = brest.gui.app:main'
          ]
    },
    install_requires=[
        'colorama>=0.4.1',
        'pyserial>=3.4',
        'PyYAML>=5.1.2',
        'Cython>=0.29.26',
        'hidapi>=0.7.99.post21',
        'crcmod>=1.7',
    ],
    extras_require={
        'docs': [
            'sphinx',
            'sphinx_rtd_theme',
            'm2r2',
        ],
        'cameras_win': [
            'pywin32',
            'opencv-python',
            'imageio',
            'imageio-ffmpeg',
        ],
        'cameras_unix': [
            'opencv-python',
            'imageio',
            'imageio-ffmpeg',
        ],
    }
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.setup
    ~~~~~~~~~~~

    Setup file for package building.

    :copyright: 2024 Bender Robotics
"""

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='brest',
    version='0.0.16',
    author='Bender Robotics',
    author_email='venglar@benderrobotics.com',
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
    python_requires='>=3.5, <4',
    entry_points={
          'console_scripts': [
              'brest.gui = brest.gui.app:main'
          ]
    },
    install_requires=[
        'colorama==0.4.6',
        'pyserial==3.5',
        'PyYAML==6.0.1',
        'Cython==0.29.36',
        'hidapi==0.14.0',
        'crcmod==1.7',
        'packaging==23.2',
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
        'jlink_win': [
            'pywin32',
        ]
    }
)

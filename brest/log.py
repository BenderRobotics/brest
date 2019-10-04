# -*- coding: utf-8 -*-
"""
    brest.log
    ~~~~~~~~~

    This module implements logging facility for Brest.

    :copyright: 2019 Bender Robotics
"""

import os
import sys
import platform

from colorama import Fore, Back, Style
from colorama.initialise import wrap_stream
from logging import StreamHandler

class ColoredStreamHandler(StreamHandler):

    def __init__(self, stream = None):
        StreamHandler.__init__(self, stream)

    COLORS = {
        'DEBUG'  : Fore.CYAN,
        'INFO'   : Fore.GREEN,
        'WARNING': Fore.YELLOW + Style.BRIGHT,
        'ERROR'  : Fore.RED + Style.BRIGHT,
    }

    def emit(self, record):
        message = self.format(record)
        try:
            self.stream.write(self.COLORS[record.levelname] + message + Style.RESET_ALL + '\n')
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def colored_handler_factory():
    on_windows = platform.system() == 'Windows'
    on_gitlab_ci = os.environ.get('GITLAB_CI', False)

    if on_windows and not on_gitlab_ci:
        log_stream = wrap_stream(sys.stdout, None, None, None, True)
    else:
        log_stream = sys.stdout

    return ColoredStreamHandler(log_stream)

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'br_base_f': {
            'format': '[%(asctime)s][%(levelname)s] : %(class_name)s.%(funcName)s() -> %(message)s',
        },
    },
    'handlers': {
        'br_console_h': {
            '()': 'brest.log.colored_handler_factory',
            'level': 'INFO',
            'formatter': 'br_base_f',
        },
        'br_console_dbg_h': {
            '()': 'brest.log.colored_handler_factory',
            'level': 'DEBUG',
            'formatter': 'br_base_f',
        },
    },
    'loggers': {
        'brest': {
            'level': 'DEBUG',
            'handlers': ['br_console_dbg_h'],
            'propagate': False
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['br_console_h'],
        },
    },
}

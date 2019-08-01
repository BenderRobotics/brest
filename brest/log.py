import os
import sys
import platform

from colorama import Fore, Back, Style
from colorama.initialise import wrap_stream
from logging import StreamHandler

class ColoredStreamHandler(StreamHandler):

    def __init__(self, stream = None):
        super().__init__(stream)

    COLORS = {
        'DEBUG'  : Fore.CYAN,
        'INFO'   : Fore.GREEN,
        'WARNING': Fore.YELLOW + Style.BRIGHT,
        'ERROR'  : Fore.RED + Style.BRIGHT,
    }

    def emit(self, record):
        message = self.format(record)
        try:
            self.stream.write(self.COLORS[record.levelname] + message + Style.RESET_ALL)
            self.stream.write('\n')
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def coloredHandlerFactory():
    on_windows = platform.system() == 'Windows'
    on_appveyor = os.environ.get('APPVEYOR', False)

    if on_windows and not on_appveyor:
        log_stream = wrap_stream(sys.stdout, None, None, None, True)
    else:
        log_stream = sys.stdout

    return ColoredStreamHandler(log_stream)
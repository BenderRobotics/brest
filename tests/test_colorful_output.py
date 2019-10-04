import os
import sys
import logging

sys.path.insert(0, os.path.abspath('..'))
import brest

l = logging.getLogger('brest')
la = {'class_name': __name__}
l.error('Log message', extra=la)
l.warning('Log message', extra=la)
l.info('Log message', extra=la)
l.debug('Log message', extra=la)

import logging
import brest

l = logging.getLogger('brest')
la = {'class_name': __name__}
l.error('Log message', extra=la)
l.warning('Log message', extra=la)
l.info('Log message', extra=la)
l.debug('Log message', extra=la)
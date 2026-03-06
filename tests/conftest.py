from logging import handlers
import os
import sys
import logging
import datetime


path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

# setting up the logging system
DATE_STR = datetime.date.today().isoformat()
TIME_STR = datetime.datetime.now().time().strftime('%H-%M-%S')
LOG_FOLDER = os.path.join('log', '%s' % (DATE_STR))
LOG_FORMAT_FILE = '%(asctime)s %(levelname)s [%(module)s:%(funcName)s:%(lineno)d] %(message)s'

# fetch the root logger and set INFO level
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create a stream handler
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(LOG_FORMAT_FILE))
logger.addHandler(ch)

# set up the directory
if not os.path.lexists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
if not os.path.isdir(LOG_FOLDER):
    raise Exception('Could not write to log directory %s. Aborting.' % LOG_FOLDER)

# create a file handler
fh = logging.FileHandler(os.path.join(LOG_FOLDER, '%s_%s.log' % (DATE_STR, TIME_STR)))
fh.setFormatter(logging.Formatter(LOG_FORMAT_FILE))
logger.addHandler(fh)

print(logger.handlers)

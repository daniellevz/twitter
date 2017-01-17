import logging, sys
from ..config import config

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(logFormatter)
fh = logging.FileHandler('/var/log/twitter/saver.log')
fh.setFormatter(logFormatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.addHandler(fh)
logging.getLogger('pika').setLevel(logging.INFO)

config.log = logger

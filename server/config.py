from attrdict import AttrDict
import logging, sys
from twitter.config import config
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
fh = logging.FileHandler('/var/log/twitter/server.log')
fh.setFormatter(logFormatter)
fh.setLevel(logging.DEBUG)

config.log.addHandler(fh)

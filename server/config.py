from attrdict import AttrDict
import logging, sys

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(logFormatter)
fh = logging.FileHandler('/var/log/twitter/server.log')
fh.setFormatter(logFormatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.addHandler(fh)

config = AttrDict(
    log = logger, 
    general = AttrDict(
        mq_host     = 'mq',
        mq_user     = 'guest',
        mq_password = 'guest',
    ),
    server = AttrDict(
        host     = '0.0.0.0',
        port     = 80,
        commands_dir = '/home/user/projects/twitter/server/commands',
        default_disconnect_time = 10,
    ),
)
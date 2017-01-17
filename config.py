from attrdict import AttrDict
import logging, sys

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(logFormatter)
logger.addHandler(ch)
logging.getLogger('pika').setLevel(logging.INFO)
config = AttrDict(
    log = logger, 
    server = AttrDict(
        host     = '0.0.0.0',
        port     = 80,
        commands_dir = '/home/user/projects/twitter/server/commands',
        default_disconnect_time = 10,
    ),
    mq = AttrDict(
        events_exchange             = 'events',
        products_exchange           = 'products',
        events_info_routing_key     = 'info',
        events_error_routing_key    = 'error',
        host                        = 'mq',
        port                        = 5672,
        username                    = 'guest',
        password                    = 'guest',
        default_no_pika_sleeptime   = 10,
    ),
)

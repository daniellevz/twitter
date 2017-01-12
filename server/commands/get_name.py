import random

def command(name, priority=0, matcher = None):
    def decorator(f):
        f.__command__ = name
        f.__priority__ = priority 
        if callable(matcher):
            f.__matcher__ = matcher
        else:
            f.__matcher__ = lambda x: True
        return f
    return decorator
def reactor(name):
    def decorator(f):
        f.__reactor__ = name
        return f
    return decorator

@command('get_name', 10)
def build_get_name(context, client_id):
    return 'full_name', 200

#@reactor('get_name')
def react_get_name(context, client_id, data):
    # save data
    # write to log
    if data == 'emma':
        context.log.info('annoying client. disconnecting')
        return 'disconnect'
    else:
        return None

@command('tweet', 4)
def build_tweet(context, client_id):
    return 'tweet', 200

@reactor('tweet')
def reactor_tweet(context, client_id, data):
    if data.decode() == 'good night':
        context.log.info('tired of this client..')
        return None
    else:
        return 'tweet'
    
@command('disconnect')
def build_disconnect(context, client_id):
    # num seconds to disconnec to
    return '10', 440

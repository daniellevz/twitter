from .utils import now

# todo make this receive dict and create data
def create_event_data(event, client_id, **kwds):
    d = dict(
                time        = now(),
                client_id   = client_id,
                event       = event,
        )
    d.update(kwds)
    return d

def create_product_data(client_id, command, data):
    return dict(
                time        = now(),
                client_id   = client_id,
                command     = command,
                data        = data.decode()
        )

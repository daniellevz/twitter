from .utils import now
from ..model import Exchange

# todo make this receive dict and create data
def create_event_data(context, event, client_id, client_name=None):
    message_format = '{{"time": {time}, "event": {event}, "client": {{"client_id": {client_id}, "client_name": {client_name}}}}}'
    if client_name is None:
        client_name = context.connected_clients.get(client_id, '')
    return message_format.format(time=now(), event=event, client_id=client_id, client_name=client_name)

def create_product_data(context, command, data, client_id, client_name=None):
    message_format = '{{"time": {time}, "command": {command}, "data": {data}, "client": {{"client_id": {client_id}, "client_name": {client_name}}}}}'
    if client_name is None:
        client_name = context.connected_clients.get(client_id, '')
    return message_format.format(time=now(), command=command, data=data, client_id=client_id, client_name=client_name)


def publish_event(context, event, client_id, level=None):
    if level is None:
        level = config.default_event_level

class EventExchange(Exchange):

    def publish(self, context, routing_key, event, client_id, client_name=None):
        body  = create_event_data(context, event, client_id, client_name)
        super(EventExchange, self).publish(routing_key, body)

class ProductExchange(Exchange):
    
    def publish(self, context, routing_key, command, data, client_id, client_name=None):
        body  = create_product_data(context, command, data, client_id, client_name)
        super(ProductExchange, self).publish(routing_key, body)

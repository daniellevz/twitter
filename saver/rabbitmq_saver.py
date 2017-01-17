import datetime, django, json, os, pika
from .config import config
from .rabbitmq import Connection, Exchange

os.environ['DJANGO_SETTINGS_MODULE'] = 'twitter.saver.saver.settings'
django.setup()

from twitter.saver.responses.models import Response

print(1)
con = Connection(config.mq.host)
print(2)
events_exchange = Exchange(con, config.mq.events_exchange)
products_exchange = Exchange(con, config.mq.products_exchange)
print(products_exchange)

@events_exchange.subscriber('*')
def printer(channel, method, properties, body):
    print ('EVENTS:  received %s' %body)

@products_exchange.subscriber('*.*')
def printer(channel, method, properties, body):
    print(body, type(body))
    print(body.decode(), type(body.decode()))
    r = json.loads(body.decode())
    created_time = datetime.datetime.fromtimestamp(r['time']).strftime('%Y-%m-%d %H:%M:%S')
    response = Response(client_id=r['client']['client_id'], command=r['command'], data=r['data'], created_time=created_time)
    response.save()
    print ('received %s' %body)

products_exchange.start_consuming()

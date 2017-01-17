import pika
#credentials = pika.PlainCredentials('user', 'user')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='mq'))
channel = connection.channel()
#exchange_name = 'events'
exchange_name = 'products'
channel.exchange_declare(exchange=exchange_name, type='topic')
queue_name = 'test4'
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='*')
def callback(ch, method, properties, body):
    print('received %s' % body)

channel.basic_consume(callback, queue=queue_name, no_ack=True)
channel.start_consuming()

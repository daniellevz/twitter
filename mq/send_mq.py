import pika
#credentials = pika.PlainCredentials('user', 'user')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='mq'))
channel = connection.channel()
exchange_name = 'products'
channel.exchange_declare(exchange=exchange_name, type='topic')
message = 'Hello world'
channel.basic_publish(exchange=exchange_name,
                      routing_key='1.2',
                      body=message,
                      )
print('send %s on %s exchang' % (message, exchange_name))
connection.close()

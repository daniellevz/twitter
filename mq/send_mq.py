import pika
#credentials = pika.PlainCredentials('user', 'user')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='mq'))
channel = connection.channel()
channel.exchange_declare(exchange='received', type='topic')
message = 'Hello world'
channel.basic_publish(exchange='received',
                      routing_key='greeting',
                      body=message,
                      )
print('send %s on %s exchang' % (message, 'received'))
connection.close()

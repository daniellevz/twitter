from .mq import MQ

class Exchange:
    
    def __init__(self, mq, exchange_name, exchange_type):
        '''tries to declare exchange with these params. willl raise pika.exception.ChannelClosed if cannot (for example if exchange with this name but of a different type exists'''
        self.mq = mq
        self.exchange_name  = exchange_name
        self.exchange_type  = exchange_type
        self.setup_exchange()

    def setup_exchange(self):
        self.mq.channel.exchange_declare(exchange=self.exchange_name, type=self.exchange_type)
    
    def publish(self, routing_key, body):
        self.mq.channel.basic_publish(exchange=self.exchange_name,
                                      routing_key=routing_key,
                                      body=body)

import pika, time

default_no_pika_sleeptime = 10

class MQ:
    
    def __init__(self, host):
        self.host        = host    
        self._connection = None
        self._channel    = None
    
    @property
    def connection(self):
        if self._connection is not None and self._connection.is_open:
            print('have connection')
            return self._connection
        elif self._connection is not None:
            self._connection.close()
            self._connection = None
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
                return connection
            except pika.exceptions.ConnectionClosed:
                print('cannot get pika channel. sleeping %s seconds' % default_no_pika_sleeptime)
                time.sleep(default_no_pika_sleeptime)
            except:
                print('can not connect to pika')
                raise
    @property
    def channel(self):
        if self._channel is not None and self._channel.is_open:
            return self._channel
        if self._channel is not None:
            self._channel = None
        self._channel = self.connection.channel()
        return self._channel

    def close(self):
        if self._channel is not None:
            self._channel.close()
            self._channel = None
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def delete_exchange(self, exchange):
        self.channel.exchange_delete(exchange=exchange) 

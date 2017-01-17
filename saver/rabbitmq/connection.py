import pika, time, traceback

default_username = 'guest'
default_password = 'guest'
default_port     = 5672

class Connection:
     
    def __init__(self, host, port=None, username=None, password=None):
        self.host       = host 
        self.port       = port if port is not None else default_port
        self.username   = username if username is not None else default_username
        self.password   = password if password is not None else default_password
        self.connect()

    def connect(self, persistent=None):
        if persistent is None:
            persistent = True
        while True:
            try:
                self._connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host        = self.host,
                    port        = self.port,
                    credentials = pika.credentials.PlainCredentials(
                        username    = self.username,
                        password    = self.password,
                    )
                ))
                return
            except pika.exceptions.AMQPError:
                if not persistent:
                    break
                time.sleep(1)

    def close(self):
        self._connection.close()

    def channel(self):
        return self._connection.channel()

    def reconnect(self, persistent=None):
        if self._connection is not None and self._connection.is_open:
            self._connection.close()
        self.connect()

    def _execute(self, func, on_reconnect):
        while True:
            try:
                return func()
            except pika.exceptions.AMQPError:
                traceback.print_exc()
                self.reconnect()
                on_reconnect()


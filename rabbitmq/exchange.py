import collections, json, pika, traceback

Consumer = collections.namedtuple('Consumer', 'func queue binding_key no_ack')

class Exchange:
    
    def __init__(self, context, connection, name):
        self.context        = context
        self.connection     = connection
        self.channel        = self.execute(self.connection.channel)
        self._exchange      = name
        self.consumers      = []
        self._exchange_declare()

    def execute(self, func):
        return self.connection._execute(func, self._restore)

    def _exchange_declare(self):
        self.execute(lambda: self.channel.exchange_declare(
            exchange    = self._exchange, 
            type        = 'topic',
        ))

    def _queue_initialize(self, binding_key, name=None):
        if name is None:
            result = self.channel.queue_declare(exclusive=True)
            name = result.method.queue
        else:
            self.channel.queue_declare(queue=name)
        self.execute(lambda: self.channel.queue_bind(
            exchange    = self._exchange, 
            queue       = name,
            routing_key = binding_key,
        ))
        return name

    def _restore(self):
        self.channel    = self.connection.channel()
        self.exchange   = self.channel.exchange_declare(exchange=self._exchange, type='topic')
        for consumer in self.consumers:
            consumer.queue = self._queue_initialize(consumer.binding_key, consumer.queue)
            self.execute(lambda: self.channel.basic_consume(
                exchange    = self._exchange,
                queue       = consumer.queue,
                no_ack      = consumer.no_ack,
            ))

    def publish(self, routing_key, json_message):
        message = json.dumps(json_message)
        self.execute(lambda: self.channel.basic_publish(
            exchange    = self._exchange,
            routing_key = routing_key,
            body        = message,
        ))

    def subscriber(self, binding_key, name=None, no_ack=None):
        if no_ack is None:
            no_ack = True
        def decorator(func):
            def callback(channel, method, properties, body):
                try:
                    func(channel, method, properties, body)
                except:
                    traceback.print_exc()
            queue = self._queue_initialize(binding_key, name)
            consumer = Consumer(callback, queue, binding_key, no_ack)
            self.execute(lambda: self.channel.basic_consume(
                consumer_callback   = callback,
                queue               = consumer.queue,
                no_ack              = consumer.no_ack,
            ))
            self.consumers.append(consumer)
        return decorator

    def start_consuming(self):
        self.execute(self.channel.start_consuming)
        
    def stop_consuming(self):
        self.execute(self.channel.stop_consuming)

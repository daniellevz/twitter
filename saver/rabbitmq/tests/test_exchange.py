import pika, pytest, sys, tash.config, tash.rabbitmq, threading, time

rabbitmq_configuration = tash.config.configuration.rabbitmq
connection = tash.rabbitmq.Connection(
    host        = rabbitmq_configuration.host,
    port        = rabbitmq_configuration.port,
    username    = rabbitmq_configuration.username,
    password    = rabbitmq_configuration.password,
)

foo_counter = 0
bar_counter = 0

@pytest.fixture
def exchange(request):
    return tash.rabbitmq.Exchange(connection, 'test_exchange')

def _publish(exchange, routing_key, message, func):
    exchange.publish(routing_key, message)
    time.sleep(1)
    func()

def test_publish(exchange):
    f = foo_counter
    b = bar_counter

    @exchange.subscriber('foo.#')
    def foo(channel, method, properties, body):
        global foo_counter
        foo_counter += 1

    @exchange.subscriber('*.bar', name='bar')
    def bar(channel, method, properties, body):
        global bar_counter
        bar_counter += 1

    def foobar_asserts(f, b):
        assert foo_counter == f
        assert bar_counter == b

    exchange.connection._connection.add_timeout(10, sys.exit)
    t = threading.Thread(target=exchange.start_consuming)
    t.start()

    _publish(exchange, 'hello.world', 'hello world', lambda: foobar_asserts(f, b))
    _publish(exchange, 'foo.bar', 'foobar', lambda: foobar_asserts(f + 1, b + 1))
    _publish(exchange, 'foo.hello.world', {'foo': 'hello world'}, lambda: foobar_asserts(f + 2, b + 1))
    _publish(exchange, 'hello.bar', {'hello': 'bar'}, lambda: foobar_asserts(f + 2, b + 2))

    exchange.stop_consuming()
    t.join(1)


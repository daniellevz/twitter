import pika, pytest, tash.config, tash.rabbitmq

@pytest.fixture
def connection(request):
    rabbitmq_configuration = tash.config.configuration.rabbitmq
    con = tash.rabbitmq.Connection(
        host        = rabbitmq_configuration.host,
        port        = rabbitmq_configuration.port,
        username    = rabbitmq_configuration.username,
        password    = rabbitmq_configuration.password,
    )
    def teardown():
        con.close()
    return con

on_reconnect = 0
raised       = False

def _on_reconnect():
    global on_reconnect
    on_reconnect += 1

def _raise_once():
    global raised
    if not raised:
        raised = True
        raise pika.exceptions.AMQPError

def test_live(connection):
    assert connection._connection.is_open == True
    
def test_reconnect(connection):
    connection.reconnect()
    assert connection._connection.is_open == True

def test_reconnect_on_execute(connection):
    o_r = on_reconnect
    connection._execute(_raise_once, _on_reconnect)
    assert on_reconnect == o_r + 1

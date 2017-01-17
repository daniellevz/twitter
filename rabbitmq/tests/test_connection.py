import pika, pytest
from twitter.config import config
from twitter.rabbitmq import Connection

@pytest.fixture
def connection(request):
    con = Connection(
        host        = config.mq.host,
        port        = config.mq.port,
        username    = config.mq.username,
        password    = config.mq.password,
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

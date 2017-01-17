import flask, json, logging, random
from flask import request
from .config import config
from .context import Context
from twitter.rabbitmq import Connection, Exchange
from .utils import create_product_data, create_event_data 
from .utils import *

# todo remove idea of name+id (stay only with name)
# make states more comfortable 

app = flask.Flask(__name__)
context = Context() 
states = {} # client_id: state
connected_clients = {} # client_name to id
commands, reactors = utils.load_commands(context, config.server.commands_dir) #list of ordered commands and dict of reactor_name:reactor
context.update(dict(
    log                 = config.log, 
    states              = states, 
    connected_clients   = connected_clients,
    commands            = commands,
    reactors            = reactors,
    ))

@app.route('/connect/<name>')
def get_connect_command(name):
    config.log.info('%s trying to connect' % name)
    if name in connected_clients.keys():
        config.log.warn('%s already connected' % name)
        event_data = create_event_data(connected_clients[name], 'client_already_connected', name=name)
        context.events_exchange.publish('warn', event_data)
        return '%s is already connected. use your id' % name, 403
    client_id = random.randrange(10000)
    while client_id in connected_clients.values():
        client_id = random.randrange(10000)
    connected_clients[name] = client_id
    states[client_id] = 0
    config.log.debug('%s received id %s' % (name, client_id))
    config.log.debug('%s state is now 0' % (client_id))
    command, status = utils.get_command(context, client_id)
    data = {'client_id': client_id, 'command': command}
    event_data = create_event_data(client_id, 'new_client_connected')
    context.events_exchange.publish('info', event_data)
    config.log.info('sending data  %s' % data)
    return flask.jsonify(data), status

@app.route('/submit', methods=['POST'])
def get_submit():
    client_id = int(request.args['client_id'])
    if client_id not in states:
        config.log.error('client with unknown id connected. sending disconnect')
        event_data = create_event_data(client_id, 'client with unknown id connected')
        context.events_exchange.publish('error', event_data)
        command, status = utils.disconnect_client(context, client_id)
        return flask.jsonify(dict(command=command)), status 
    data = request.data
    event_data = create_event_data(client_id, 'received_submit', data=data.decode())
    context.events_exchange.publish('info', event_data)
    command_name = commands[states[client_id]].__command__
    product_data = create_product_data(client_id, command_name, data)
    context.products_exchange.publish('%s.%s' % (command_name, client_id), product_data)
    config.log.info('received submit from client %s for data %s' % (client_id, data))
    # get user_id
    new_command =utils.run_reactor(context,client_id, data)
    if new_command is not None:
        config.log.info('reactor wants to run %s' % new_command)
        command = utils.get_command_by_name(context, new_command)
        if utils.run_matcher(context, command, client_id):
            command, status = utils.run_command(context, command, client_id)
            return flask.jsonify(dict(command=command)), status
        else:
            config.log.info('reactors build did not match on %s' % client_id)
    else:
        config.log.info('command has no reactor moving on to next command')
    states[client_id] += 1 
    command, status = utils.get_command(context, client_id)
    event_data = create_event_data(client_id, 'sending_command: %s' % command, command=command)
    context.events_exchange.publish('info', event_data)
    if isinstance(command, dict):
        return flask.jsonify(command), status
    else:
        data = dict(command=command)
        return flask.jsonify(data), status

def run():
    config.log.info('starting')
    con = Connection(config.mq.host)
    context.products_exchange   = Exchange(context, con, config.mq.products_exchange)
    context.events_exchange     = Exchange(context, con, config.mq.events_exchange)
    app.run(config.server.host, config.server.port)


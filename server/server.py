import flask, json, logging, random
from flask import request
from .utils import EventExchange
from .config import config
from .context import Context
from .model import *
from .utils import *
 
app = flask.Flask(__name__)
context = Context() 
states = {}# client_id: state
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
        context.events_exchange.publish(context, 'warn', 'client_already_connected', connected_clients[name], name)
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
    context.events_exchange.publish(context, 'info', 'new_client_connected', client_id, name)
    config.log.info('sending data  %s' % data)
    return flask.jsonify(data), status

@app.route('/submit', methods=['POST'])
def get_submit():
    client_id = int(request.args['client_id'])
    if client_id not in states:
        config.log.error('client with unknow id connected. sending disconnect')
        command, status = utils.disconnect_client(context, client_id)
        return flask.jsonify(dict(command=command)), status 
    data = request.data
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
    if isinstance(command, dict):
        return flask.jsonify(command), status
    else:
        data = dict(command=command)
        return flask.jsonify(data), status

def run():
    config.log.info('starting')
    mq = MQ(config.mq.host)
    context.events_exchange = EventExchange(mq, 'events', 'topic')
    context.products_exchange = Exchange(mq, config.mq.products_exchange, 'topic')
    app.run(config.server.host, config.server.port)


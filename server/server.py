import flask, json, logging, random
from flask import request
from attrdict import AttrDict
from config import config
from utils import load_commands
app = flask.Flask(__name__)

states = {}# client_id: state
connected_clients = {} # client_name to id
commands, reactors = load_commands() #list of ordered commands and dict of reactor_name:reactor
context = AttrDict({'log': config.log})

def get_command(client_id):
    state = states[client_id]        
    command = commands[state]
    while not run_matcher(context, command, client_id):
        state = +1
        command = commands[state]
    config.log.info('found command %s for client %s' % (command.__command__, client_id))
    return run_command(context, command, client_id)

def run_matcher(context, command, client_id):
    if not command.__matcher__(client_id):
        context.log.info('command %s did not match on client %s' % (command.__command__, client_id))
        return False
        context.log.info('command %s DID match on client %s' % (command.__command__, client_id))
    return True

def run_command(context, command, client_id):
    context.log.info('client %s checking command %s' % (client_id, command.__command__))
    response = command(context, client_id)
    context.log.info('sending to client %s' % json.dumps(response))
    _, status = response
    if status != 200:
        delete_client(client_id)
    return response

def get_command_by_name(name):
    for b in commands:
        if b.__command__ == name:
            return b
    raise ValueError('no command with name %s exists' % name)

def delete_client(client_id):
    for k, v in connected_clients.items():
        if v == client_id:
            connected_clients.pop(k)
            break
    states.pop(client_id)

def disconnect_client(client_id):
    delete_client(client_id)
    return config.server.default_disconnect_time, 440

@app.route('/connect/<name>')
def get_connect_command(name):
    config.log.info('%s trying to connect' % name)
    if name in connected_clients.keys():
        config.log.warn('%s already connected' % name)
        return '%s is already connected. use your id' % name, 403
    client_id = random.randrange(10000)
    while client_id in connected_clients.values():
        client_id = random.randrange(10000)
    connected_clients[name] = client_id
    states[client_id] = 0
    config.log.debug('%s received id %s' % (name, client_id))
    config.log.debug('%s state is now 0' % (client_id))
    command, status = get_command(client_id)
    print(command)
    data = {'client_id': client_id, 'command': command}
    config.log.info('sending data  %s' % data)
    return flask.jsonify(data), status

def run_reactor(client_id, data):
    command_name = commands[states[client_id]].__command__
    if command_name in reactors:
        reactor = reactors[command_name]
        config.log.info('have reactor to run')
        try:
            data = reactors[command_name](context,client_id, data)
            return data
        except ValueError:
            config.log.exception()
            return None
    config.log.info('no reactor to run..')
    return 

@app.route('/submit', methods=['POST'])
def get_submit():
    client_id = int(request.args['client_id'])
    if client_id not in states:
        config.log.error('client with unknow id connected. sending disconnect')
        command, status = disconnect_client(client_id)
        return flask.jsonify(dict(command=command)), status 
    data = request.data
    config.log.info('received submit from client %s for data %s' % (client_id, data))
    # get user_id
    new_command = run_reactor(client_id, data)
    if new_command is not None:
        config.log.info('reactor wants to run %s' % new_command)
        command = get_command_by_name(new_command)
        if run_matcher(context, command, client_id):
            command, status = run_command(context, command, client_id)
            return flask.jsonify(dict(command=command)), status
        else:
            config.log.info('reactors build did not match on %s' % client_id)
    else:
        config.log.info('command has no reactor moving on to next command')
    states[client_id] += 1 
    command, status = get_command(client_id)
    if isinstance(command, dict):
        return flask.jsonify(command), status
    else:
        data = dict(command=command)
        return flask.jsonify(data), status

if __name__ == '__main__':
    config.log.info('starting')
    app.run(config.server.host, config.server.port)


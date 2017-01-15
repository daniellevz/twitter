import json, imp, os, time, unipath

ordered_commands = []
commands = {}
reactors = {}

def now():
    return int(time.time())
def load_commands(context, commands_dir):
    directory = unipath.Path(commands_dir)
    for f in directory.listdir(filter=unipath.FILES, pattern = '*.py'):
        name = unipath.Path(f).stem
        m = imp.new_module(name) # filename is module name
        with open(f) as reader:
            data = reader.read()
        try:
            exec(data, m.__dict__)
        except SyntaxError:
            context.log.exception('error loading %s. skipping file' % name)
        for i in m.__dict__:
            if getattr(m.__dict__[i], '__command__', None):
                if i in commands:
                    raise ValueError('more than one command with name %s' % name)
                commands[i] = dict(priority = m.__dict__[i].__priority__, command = m.__dict__[i])
            elif getattr(m.__dict__[i], '__reactor__', None):
                if i in reactors:
                    raise ValueError('more than one reactor with name %s' % name)
                reactors[m.__dict__[i].__reactor__] = m.__dict__[i]
    for key, value in sorted(commands.items(), key=lambda kv: kv[1]['priority'], reverse=True):
        ordered_commands.append(value['command'])
    return ordered_commands, reactors

def get_command_by_name(context, name):
    '''return the command function with that name. if no such command exists raises ValueError'''
    for b in context.commands:
        if b.__command__ == name:
            return b
    raise ValueError('no command with name %s exists' % name)

def get_command(context, client_id):
    '''receives a client_id and runs the next command, returning the output (command, status). the function gets the clients state and iterates over the next commands until it finds one where the matcher returns True- sending the output of this command to the client'''
    state = context.states[client_id]        
    command = context.commands[state]
    while not run_matcher(context, command, client_id):
        state = +1
        command = context.commands[state]
    context.log.info('found command %s for client %s' % (command.__command__, client_id))
    return run_command(context, command, client_id)

def run_command(context, command, client_id):
    '''receives the commannd to run and the client. runs the command and if the status is not 200, deletes the client (deletes the state) and sends to the client what the command returned'''
    context.log.info('client %s checking command %s' % (client_id, command.__command__))
    response = command(context, client_id)
    context.log.info('sending to client %s' % json.dumps(response))
    _, status = response
    if status != 200:
        delete_client(context, client_id)
    return response

def run_matcher(context, command, client_id):
    '''receives a command and a client_id and runs the command.__matcher__ which decides if the command is relevant to this client. returns True/False'''
    if not command.__matcher__(client_id):
        context.log.info('command %s did not match on client %s' % (command.__command__, client_id))
        return False
        context.log.info('command %s DID match on client %s' % (command.__command__, client_id))
    return True

def run_reactor(context, client_id, data):
    '''receives client_id and data, checks which command returned this data and if it declared a reactor, runs it. The reactor returns a command name, its matcher runs, and if the matcher returns True- this command is send to the client otherwise None is returned'''
    command_name = context.commands[context.states[client_id]].__command__
    if command_name in context.reactors:
        reactor = context.reactors[command_name]
        context.log.info('have reactor to run')
        try:
            data = context.reactors[command_name](context,client_id, data)
            return data
        except ValueError:
            context.log.exception()
            return None
    context.log.info('no reactor to run..')
    return 

def delete_client(context, client_id):
    '''deletes client from connected clients and deletes its state'''
    for k, v in context.connected_clients.items():
        if v == client_id:
            context.connected_clients.pop(k)
            break
    context.states.pop(client_id)

def disconnect_client(context, client_id):
    '''deletes client and also sends disconnect. can be used if error occured or client has swayed from protocol'''
    delete_client(context, client_id)
    return context.server.default_disconnect_time, 440

if __name__ == '__main__':
    print(dir())
    load_commands()

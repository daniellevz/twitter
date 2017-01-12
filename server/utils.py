import imp, os, unipath
from config import config

ordered_commands = []
commands = {}
reactors = {}
def load_commands():
    directory = unipath.Path(config.server.commands_dir)
    for f in directory.listdir(filter=unipath.FILES, pattern = '*.py'):
        name = unipath.Path(f).stem
        m = imp.new_module(name) # filename is module name
        with open(f) as reader:
            data = reader.read()
        try:
            exec(data, m.__dict__)
        except SyntaxError:
            config.log.exception('error loading %s. skipping file' % name)
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
if __name__ == '__main__':
    print(dir())
    load_commands()

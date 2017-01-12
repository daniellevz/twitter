import json, re, requests, sys
connect_re = re.compile("(\d+);(\w+)")

def connect(name):
    r = requests.get('http://127.0.0.1/connect/%s' % name)
    if r.status_code == 200:
        response = json.loads(r.text)
        client_id, command = response['client_id'], response['command']
        print('connected! got id %s and command %s' % (client_id, command))
    else:
        print('error: status: %s msg: %s' %(r.status_code, r.text))

if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv)>1 else 'alice'
    print('using name %s' % name)
    # connect
    r = requests.get('http://127.0.0.1/connect/%s' % name)
    if r.status_code == 200:
        response = json.loads(r.text)
        client_id, command = response['client_id'], response['command']
        print('connected! got id %s and command %s' % (client_id, command))
    else:
        print('error: status: %s msg: %s' %(r.status_code, r.text))
    response = command.upper()
    while r.status_code == 200:
        r = requests.post('http://127.0.0.1/submit', params={'client_id': client_id}, data=response)
        # get new command
        #submit again
    if r.status_code == 204:
        pass
        # received sleep command
        # get sleep time, sleep, reconnect

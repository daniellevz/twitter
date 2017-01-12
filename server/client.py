import json, random, re, requests, sys, time
connect_re = re.compile("(\d+);(\w+)")
tweets = ['hello!', 'good morning', 'blah', 'nothing to say', ':)', 'good night']
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
    while True:
        r = requests.get('http://127.0.0.1/connect/%s' % name)
        if r.status_code == 200:
            response = json.loads(r.text)
            client_id, command = response['client_id'], response['command']
            print('connected! got id %s and command %s' % (client_id, command))
        else:
            print('error: status: %s msg: %s' %(r.status_code, r.text))
            exit()
        send = command.upper()
        r = requests.post('http://127.0.0.1/submit', params={'client_id': client_id}, data=send)
        while r.status_code == 200:
            # get new command
            response = json.loads(r.text)
            if response['command'] == 'tweet':
                send = tweets[random.randrange(len(tweets))]
                print('got command tweet. sending: %s' % send) 
            else:
                send = r['command'] + '?'
                print('got unknown command %s. sending: %s' % (r['command'], send))
    
            r = requests.post('http://127.0.0.1/submit', params={'client_id': client_id}, data=send)
            #submit again
        if r.status_code == 440:
            print('got command disconnect')
            sleep_time = int(json.loads(r.text)['command']) 
            print('for %s seconds' % sleep_time)
            time.sleep(sleep_time)
            # received sleep command
            # get sleep time, sleep, reconnect

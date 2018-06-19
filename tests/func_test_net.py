import os
import json
import logging as log
import time
from net import hsock
from net.Peers import Peer, Peers

name = str(os.getenv('HODL_NAME'))
log.basicConfig(filename=name + '.log', level=log.DEBUG)
log.debug(
    '\n\n\n\n\n\n-------------------------------------\nstart\n-------------------------------------\n\n\n\n\n\n\n\n\n')
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]
if name == 'Alice':
    peers = Peers([Peer(keys['Bob'][1], [('172.19.0.3', 5000)]),
                   Peer(keys['Chuck'][1], [('172.19.0.4', 5000)]),
                   Peer(keys['Dave'][1], [('172.19.0.5', 5000)])])
    time.sleep(2)
if name == 'Bob':
    peers = Peers([Peer(keys['Alice'][1], [('172.19.0.2', 5000)]),
                   Peer(keys['Chuck'][1], [('172.19.0.4', 5000)]),
                   Peer(keys['Dave'][1], [('172.19.0.5', 5000)])])
if name == 'Chuck':
    peers = Peers([Peer(keys['Bob'][1], [('172.19.0.3', 5000)]),
                   Peer(keys['Alice'][1], [('172.19.0.2', 5000)]),
                   Peer(keys['Dave'][1], [('172.19.0.5', 5000)])])
if name == 'Dave':
    peers = Peers([Peer(keys['Bob'][1], [('172.19.0.3', 5000)]),
                   Peer(keys['Chuck'][1], [('172.19.0.4', 5000)]),
                   Peer(keys['Alice'][1], [('172.19.0.2', 5000)])])
port = 5000
log.debug(os.popen('ifconfig|grep inet |grep addr').read())
peers.update([my_keys], log=log)
log.debug('\n'.join([str(p.__dict__) for p in peers]))
if name == 'Bob':
    for i in range(20):
        log.debug('listen')
        try:
            s = hsock.listen()
        except Exception as e:
            log.debug('exception while listening: ' + str(e))
elif name == 'Alice':
    log.debug('creating HSock')
    s = hsock.HSock(addr=keys['Bob'][1], myaddrs=[keys['Alice']], peers=peers)

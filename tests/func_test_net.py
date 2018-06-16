import os
import json
import multiprocessing
import logging as log
from net import hsock
from net.Peers import Peer, Peers


name = str(os.getenv('HODL_NAME'))
log.basicConfig(filename=name+'.log', level=log.DEBUG)
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]
if name == 'Alice':
    peers = Peers([Peer(keys['Bob'][1], [('localhost', 5002)]),
                             Peer(keys['Chuck'][1], [('localhost', 5003)]),
                             Peer(keys['Dave'][1], [('localhost', 5004)])])
    port = 5001
if name == 'Bob':
    peers = Peers([Peer(keys['Alice'][1], [('localhost', 5001)]),
                             Peer(keys['Chuck'][1], [('localhost', 5003)]),
                             Peer(keys['Dave'][1], [('localhost', 5004)])])
    port = 5002
if name == 'Chuck':
    peers = Peers([Peer(keys['Bob'][1], [('localhost', 5002)]),
                             Peer(keys['Alice'][1], [('localhost', 5001)]),
                             Peer(keys['Dave'][1], [('localhost', 5004)])])
    port = 5003
if name == 'Dave':
    peers = Peers([Peer(keys['Bob'][1], [('localhost', 5002)]),
                             Peer(keys['Chuck'][1], [('localhost', 5003)]),
                             Peer(keys['Alice'][1], [('localhost', 5001)])])
    port = 5004

peers.update([keys['Alice']], log=log)
if name == 'Bob':
    while True:
        log.debug('listen')
        s = hsock.listen()
elif name == 'Alice':
    log.debug('creating HSock')
    s = hsock.HSock(addr=keys['Bob'][1], myaddrs=[keys['Alice']], peers=peers, log=log)

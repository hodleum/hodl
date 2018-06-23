import logging as log
import os
import json
import time
from net import hsock
from net.Peers import Peer, Peers

name = str(os.getenv('HODL_NAME'))
log.basicConfig(level=log.DEBUG)
log.debug(
    '\n\n\n\n\n\n-------------------------------------\nstart\n-------------------------------------\n\n\n\n\n\n\n\n\n')
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]


def white(peer):
    for n in peer.netaddrs:
        peer.netaddrs[n] = True
    return peer


if name == 'Alice':
    peers = Peers([white(Peer(keys['Bob'][1], [('172.19.0.3', 5000)])),
                   white(Peer(keys['Chuck'][1], [('172.19.0.4', 5000)])),
                   white(Peer(keys['Dave'][1], [('172.19.0.5', 5000)]))])
    time.sleep(2)
if name == 'Bob':
    peers = Peers([white(Peer(keys['Alice'][1], [('172.19.0.2', 5000)])),
                   white(Peer(keys['Chuck'][1], [('172.19.0.4', 5000)])),
                   white(Peer(keys['Dave'][1], [('172.19.0.5', 5000)]))])
if name == 'Chuck':
    peers = Peers([white(Peer(keys['Bob'][1], [('172.19.0.3', 5000)])),
                   white(Peer(keys['Alice'][1], [('172.19.0.2', 5000)])),
                   white(Peer(keys['Dave'][1], [('172.19.0.5', 5000)]))])
if name == 'Dave':
    peers = Peers([white(Peer(keys['Bob'][1], [('172.19.0.3', 5000)])),
                   white(Peer(keys['Chuck'][1], [('172.19.0.4', 5000)])),
                   white(Peer(keys['Alice'][1], [('172.19.0.2', 5000)]))])
if name == 'Bob':
    log.debug('Bob listen')
    for i in range(20):
        log.debug('listen')
        try:
            s = hsock.listen()
            log.debug('Bob caught a connection. Listening for a message')
            log.debug('Message: ' + s.listen_msg())
        except Exception as e:
            log.debug('exception while listening: ' + str(e))
elif name == 'Alice':
    log.debug('Alice: creating HSock to send')
    s = hsock.HSock(addr=keys['Bob'][1], myaddrs=[keys['Alice']], peers=peers)
    s.send('hi i am alice')
log.debug('func_test_net peers.update')
peers.update([my_keys])

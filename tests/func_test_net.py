import logging as log
import os
import json
import time
from net import hsock
from net.Peers import Peer, Peers

name = str(os.getenv('HODL_NAME'))
log.basicConfig(level=log.DEBUG, format='{}:%(message)s'.format(name))
log.debug(
    '\n\n\n\n\n\n-------------------------------------\nstart\n-------------------------------------\n\n\n\n\n\n\n\n\n')
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]


if name == 'Alice':
    peers = Peers([Peer(keys['Bob'][1], [('192.19.0.3', 9276)])])
    time.sleep(2)
if name == 'Bob':
    peers = Peers([Peer(keys['Alice'][1], [('192.19.0.2', 9276)])])
if name == 'Chuck':
    peers = Peers([Peer(keys['Bob'][1], [('192.19.0.3', 9276)]),
                   Peer(keys['Alice'][1], [('192.19.0.2', 9276)]),
                   Peer(keys['Dave'][1], [('192.19.0.5', 9276)])])
if name == 'Dave':
    peers = Peers([Peer(keys['Bob'][1], [('192.19.0.3', 9276)]),
                   Peer(keys['Chuck'][1], [('192.19.0.4', 9276)]),
                   Peer(keys['Alice'][1], [('192.19.0.2', 9276)])])
if name == 'Bob':
    log.debug('Bob listen')
    hsock.listen_thread()
    while len(hsock.hsocks) == 0:
        pass
    s = hsock.hsocks[0]
    log.debug('\n---------Bob caught a connection. Listening for a message. List of messages in HSock '
                                 'now: ' + str(s.in_msgs) + '-----------\n')
    if len(s.in_msgs) == 0:
        log.debug('\n\nMessage: ' + str(s.listen_msg()) + '\n\n')
    else:
        log.debug('Message was already caught: ' + str(s.in_msgs[0]))
elif name == 'Alice':
    hsock.connect_to_all(peers, keys['Alice'])
    log.debug(str(time.time()) + ': creating HSock to send')
    #s = hsock.HSock(addr=keys['Bob'][1], myaddrs=[keys['Alice']], peers=peers)
    s = hsock.connect_to(keys['Bob'][1], keys['Alice'], peers)
    s.send('hi i am alice')
    hsock.listen_thread()
else:
    hsock.listen_thread()
time.sleep(4)
log.debug('hsock.connect_to_all. time: ' + str(time.time()))
hsock.connect_to_all(peers, keys['Alice'])
time.sleep(1)
log.debug('Peers: len(peers): ' + str(len(peers)) + ',\n\n' + str(peers))
log.debug('hsocks: len=' + str(len(hsock.hsocks)) + ' hsocks=[' + '\n'.join([repr(s) for s in hsock.hsocks]) + ']')

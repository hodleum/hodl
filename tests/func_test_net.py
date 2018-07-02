import logging as log
import os
import json
import time
from threading import Thread
from net import hsock
from net.Peers import Peer, Peers


def cat_peers():
    while True:
        time.sleep(8)
        log.debug('\n\n--------------------------------------')
        log.debug(
            'Peers: len(peers): ' + str(len(peers)) + ',\n\n' + str(peers) + '\n\n------------------------------\n')


name = str(os.getenv('HODL_NAME'))
log.basicConfig(level=log.DEBUG, format='[%(asctime)s] {}:%(message)s'.format(name))
log.debug(
    '\n\n\n\n\n\n-------------------------------------\nstart\n-------------------------------------\n\n\n\n\n\n\n\n\n')
with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]

if name == 'Alice':
    peers = Peers([Peer(keys['Bob'][1], [('192.19.0.3', 9276)])])
if name == 'Bob':
    peers = Peers([Peer(keys['Chuck'][1], [('192.19.0.4', 9276)]),
                   Peer(keys['Alice'][1], [('192.19.0.2', 9276)])])
if name == 'Chuck':
    peers = Peers([Peer(keys['Bob'][1], [('192.19.0.3', 9276)]),
                   Peer(keys['Alice'][1], [('192.19.0.2', 9276)]),
                   Peer(keys['Dave'][1], [('192.19.0.5', 9276)])])
if name == 'Dave':
    peers = Peers([#Peer(keys['Bob'][1], [('192.19.0.3', 9276)]),
                   #Peer(keys['Alice'][1], [('192.19.0.2', 9276)]),
                   Peer(keys['Chuck'][1], [('192.19.0.4', 9276)])])

Thread(target=cat_peers).start()
hsock.listen_thread()
log.debug(str(time.time()) + ': listen thread started')
time.sleep(3)
hsock.connect_to_all(peers, keys['Alice'])
log.debug('\n----------\n\n' + str(time.time()) + ':\nHSock connected to all.\nHSocks: [\n'
          + '\n'.join([repr(s) for s in hsock.hsocks]) + ']\n\n--------------\n')
if name == 'Bob':
    log.debug('Bob listen')
    while len(hsock.hsocks) == 0:
        pass
    s = hsock.hsocks[0]
    log.debug('\n' + str(time.time()) + '\n---------Bob has a connection. Listening for a message. List of messages'
                                        ' in HSock now: ' + str(s.in_msgs) + '-----------\n')
    time.sleep(0.05)
    log.debug(str(s.in_msgs))
    if len(s.in_msgs) < 2:
        Thread(target=lambda: log.debug('\n\nMessage: ' + str(s.listen_msg()) + '\n\n')).start()
    else:
        log.debug('Message was already caught: ' + str(s.in_msgs[0]))
elif name == 'Alice':
    log.debug(str(time.time()) + ': creating HSock to send')
    # s = hsock.HSock(addr=keys['Bob'][1], myaddrs=[keys['Alice']], peers=peers)
    s = hsock.connect_to(keys['Bob'][1], keys['Alice'], peers)
    log.debug('hsock connected')
    s.send(data='im alice')
    pass
else:
    pass
time.sleep(0.5)
log.debug('hsock.connect_to_all. time: ' + str(time.time()))
hsock.connect_to_all(peers, keys['Alice'])
time.sleep(1)
log.debug('\n\n--------------------------------------')
log.debug('Peers: len(peers): ' + str(len(peers)) + ',\n\n' + str(peers) + '\n\n------------------------------\n')
log.debug('hsocks: len=' + str(len(hsock.hsocks)) + ' hsocks=[' + '\n'.join([repr(s) for s in hsock.hsocks]) + ']')
log.debug('--------------------------------------\n\n\n')

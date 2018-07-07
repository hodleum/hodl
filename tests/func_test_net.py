import logging as log
import os
import json
import time
from threading import Thread
from net import hsock
from net.peers import Peer, Peers


def cat_peers():
    while True:
        time.sleep(8)
        log.debug('\n\n--------------------------------------')
        log.debug(
            'Peers: len(peers): ' + str(len(peers)) + ',\n\n' + str(peers) + '\n\n------------------------------\n')


name = str(os.getenv('HODL_NAME'))

log.basicConfig(level=log.DEBUG,
                format='%(name)s.%(funcName)-8s [LINE:%(lineno)-3s]# [{}] %(levelname)-8s [%(asctime)s]'
                       '  %(message)s'.format(name))
log.debug(
    '\n\n\n\n\n\n-------------------------------------\nstart\n-------------------------------------\n\n\n\n\n\n\n\n\n')

with open('tests/keys', 'r') as f:
    keys = json.loads(f.readline())
my_keys = keys[name]

peers = Peers()
if name == 'Alice':
    peers = Peers([Peer(keys['Bob'][1], [('localhost', 9000)])])
if name == 'Bob':
    peers = Peers([Peer(keys['Chuck'][1], [('localhost', 9001)]),
                   Peer(keys['Alice'][1], [('localhost', 9002)])])
if name == 'Chuck':
    peers = Peers([Peer(keys['Bob'][1], [('localhost', 9000)]),
                   Peer(keys['Alice'][1], [('localhost', 9002)]),
                   Peer(keys['Dave'][1], [('localhost', 9003)])])
if name == 'Dave':
    peers = Peers([Peer(keys['Chuck'][1], [('localhost', 9001)])])

Thread(target=cat_peers).start()

hsock.listen_thread()
log.debug('listen thread started')

time.sleep(3)

hsock.connect_to_all(peers, keys['Alice'])

log.debug('HSock connected to all.\nHSocks: [\n' + '\n'.join([repr(s) for s in hsock.hsocks]) + ']\n\n--------------\n')

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
    s = hsock.connect_to(keys['Bob'][1], keys['Alice'], peers)
    log.debug('hsock connected')
    s.send(data='im alice')

time.sleep(0.5)

log.debug('hsock.connect_to_all. time: ' + str(time.time()))
hsock.connect_to_all(peers, keys['Alice'])
time.sleep(1)
log.debug('\n\n--------------------------------------')
log.debug('Peers: len(peers): ' + str(len(peers)) + ',\n\n' + str(peers) + '\n\n------------------------------\n')
log.debug('hsocks: len=' + str(len(hsock.hsocks)) + ' hsocks=[' + '\n'.join([repr(s) for s in hsock.hsocks]) + ']')
log.debug('--------------------------------------\n\n\n')

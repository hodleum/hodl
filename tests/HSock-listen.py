from threading import Thread
import time
import json
import logging as log
from net.hsock import HSock, listen
from net.peers import Peers, Peer


log.basicConfig(level=log.DEBUG, format='[%(asctime)s]:%(message)s')
log.debug('----------hsock-listen----------')
peer2 = Peer('2', [('localhost', 1222)])
peers1 = Peers([peer2])
peer1 = Peer('1', [('localhost', 1221)])
peers2 = Peers([peer1])


def sendertester():
    log.debug('----' + str(time.time()))
    sock = HSock(addr='1', myaddrs=(['2priv', '2'], ), peers=peers2)
    time.sleep(0.6)
    sock.send('abc')
    log.debug(str(time.time()))


def listentester():
    s = listen(1221)
    print('len(s.in_msgs)', len(s.in_msgs), s.in_msgs)
    print('\n------------------------------\n', json.loads(s.listen_msg())['message']['body'],
          '\n----------------------------')
    print('\n------------------------------\n', json.loads(s.listen_msg())['message']['body'],
          '\n----------------------------')


Thread(target=listentester, name="listener").start()
time.sleep(1)
Thread(target=sendertester, name="sender").start()

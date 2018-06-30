from threading import Thread
import time
import logging as log
from net.hsock import HSock, listen
from net.Peers import Peers, Peer


log.basicConfig(level=log.DEBUG)
log.debug('----------hsock-listen----------')
peer2 = Peer('2', [('127.0.0.1', 1222)])
peers1 = Peers([peer2])
peer1 = Peer('1', [('127.0.0.1', 1221)])
peers2 = Peers([peer1])


def sendertester():
    log.debug('----' + str(time.time()))
    sock = HSock(addr='1', myaddrs=('2', ), peers=peers2)
    time.sleep(0.6)
    sock.send('abc')
    log.debug(str(time.time()))


def listentester():
    s = listen(1221)
    print('len(s.in_msgs)', len(s.in_msgs), s.in_msgs)
    for i in range(5):
        time.sleep(0.5)
        print('len(s.in_msgs)', len(s.in_msgs), s.in_msgs)


Thread(target=listentester, name="listener").start()
time.sleep(1)
Thread(target=sendertester, name="sender").start()

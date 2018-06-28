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
    time.sleep(1)
    s = HSock(addr='1', myaddrs=('2', ), peers=peers2)
    s.send('abc')


def listentester():
    s = listen(1221)
    print('len(s.in_msgs)', len(s.in_msgs), s.in_msgs)
    print(s.listen_msg())


Thread(target=sendertester).start()
listentester()

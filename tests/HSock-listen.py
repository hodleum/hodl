from threading import Thread
import time
import logging as log
from net.hsock import HSock, listen
from net.Peers import Peers, Peer


log.basicConfig(filename='hsock-listen.log', level=log.DEBUG)
log.debug('----------hsock-listen----------')
peer2 = Peer('2', [('127.0.0.1', 1222)])
peer2.netaddrs['127.0.0.1:1222'] = True
peers1 = Peers([peer2])
peer1 = Peer('1', [('127.0.0.1', 1221)])
peer1.netaddrs['127.0.0.1:1221'] = True
peers2 = Peers([peer1])


def sendertester():
    s = HSock(addr='1', myaddrs=('2', ), peers=peers2)
    s.send('abc')


def listentester():
    s = listen(1221)
    print(s.listen_msg())


Thread(target=listentester).start()
time.sleep(0.1)
Thread(target=sendertester).start()

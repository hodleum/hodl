from threading import Thread
import time
from net.hsock import HSock, listen
from net.Peers import Peers, Peer


peers1 = Peers([Peer('2', [('localhost', 1222)])])
peers2 = Peers([Peer('1', [('localhost', 1221)])])


def sendertester():
    s = HSock(addr='1', myaddrs=('2', ), peers=peers2)
    s.send('abc')


def listentester():
    s = listen(1221)
    print(s.listen_msg())


Thread(target=listentester).start()
time.sleep(0.1)
Thread(target=sendertester).start()

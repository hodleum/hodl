import logging as log
from net.peers import Peers, Peer
import net
from sync.Connections import InputConnection, Connection
from _thread import start_new_thread


peers = Peers()
default_port = 7080
conns = []


def get_sc_memory(index, start=0, stop=-1):
    mem = []
    # todo
    return mem


def get_block(index):
    pass
    # todo


def listen_loop(keys):
    while True:
        sock = net.listen()
        log.debug('net.listen_loop: input connection in listen loop')
        conns.append(InputConnection(sock, keys))


def send_loop(keys):
    while True:
        log.debug('net.send_loop')
        for peer in list(peers):
            try:
                conns.append(Connection(peer, keys, peers, log=log))
            except:
                peers.remove(peer)


def loop(keys, port=default_port):
    log.debug('net.loop')
    start_new_thread(listen_loop, args=(keys, log))
    log.debug('net.loop: started listen_loop')
    send_loop(keys)
    log.debug('net.loop: started send_loop')

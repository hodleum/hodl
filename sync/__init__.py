"""
It synchronizes blockchain between HODL peers.
Algorthm:
The first user sends last block and blockchain's length to the other.
The second user sends delta between their blockchains' lengths, and if his blockchain is longer, sends 1000 or less blocks to first user.
The first user sends blocks if his blockchain is longer.
User checks blocks he accepted by getting the same blocks from other users (get_many_blocks), and if |delta|>1000, gets missing blocks
"""
import logging as log
from net.Peers import Peers, Peer
import net
from sync.Connections import *


global peers
peers = Peers()
default_port = 7080
global conns
conns = []


def get_sc_memory(index, start=0, stop=-1):
    mem = []
    # todo
    return mem


def get_block(index):
    pass
    # todo


def listen_loop(keys, log=None):
    while True:
        sock = net.listen()
        if log:
            log.debug('input connection in listen loop')
        conns.append(InputConnection(sock, keys, log=log))


def send_loop(keys, log=None):
    while True:
        for peer in list(peers):
            try:
                conns.append(Connection(peer, keys, peers, log=log))
            except:
                peers.remove(peer)


def loop(keys, port=default_port, log=None):
    name = 'Alice'
    proc = multiprocessing.Process(target=listen_loop, args=(keys, log))
    proc.start()
    proc.join()
    send_loop(keys)

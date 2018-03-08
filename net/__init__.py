"""
It synchronizes blockchain between HODL peers.
Algorшthm:
The first user sends last block and blockchain's length to the other.
The second user sends delta between their blockchains' lengths, and if his blockchain is longer, sends 1000 or less blocks to first user.
The first user sends blocks if his blockchain is longer.
User checks blocks he accepted by getting the same blocks from other users (get_many_blocks), and if |delta|>1000, gets missing blocks
"""
import block
import socket
import multiprocessing
import json
from net.Peers import *
from net.Connections import *


global peers
peers = Peers()
default_port = 6666
global conns
conns = []


def loop():
    while True:
        for peer in peers:
            try:
                conns.append(Connection(peer[0], peer[1]))
            except:
                peers.remove(peer)

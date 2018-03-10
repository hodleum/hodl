"""
It synchronizes blockchain between HODL peers.
Algorthm:
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
default_port = 5000
global conns
conns = []


def get_sc_memory(index, start=0, stop=-1):
    mem = []
    return mem


def listen_loop(privkey, pubkey, port=default_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen(1)
    conn, addr = sock.accept()
    conns.append(InputConnection(conn, privkey, pubkey))


def send_loop(privkey, pubkey):
    while True:
        for peer in peers:
            try:
                conns.append(Connection(peer[0], peer[1], privkey, pubkey))
            except:
                peers.remove(peer)


def loop(privkey, pubkey, port=default_port):
    proc = multiprocessing.Process(target=listen_loop, args=(privkey, pubkey, port))
    proc.start()
    proc.join()
    send_loop(privkey, pubkey)

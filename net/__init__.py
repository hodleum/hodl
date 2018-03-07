"""
It synchronizates blockchain between HODL peers.
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


def get_many_blocks(minb, maxb):
    pass


def handle_request(req):
    ans = []
    return ans


def loop():
    while True:
        for peer in peers:
            try:
                conns.append(Connection(peer[0], peer[1]))
            except:
                peers.remove(peer)

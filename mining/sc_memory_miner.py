import block
import cryptogr as cg
import json


def calculate_hash(mem, addr):
    h = cg.h(json.dumps((mem.local, addr)))
    return h


def start_mining_sc(bch, scind, addr):
    bch[scind[0]].contracts[scind[1]].memory.peers.append(addr)

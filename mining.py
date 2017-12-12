import block
import time
import cryptogr as cg


#todo: write mining

def pow_mine(bch, b):
    """proofs-of-work mining"""
    miners = bch[-1].powminers
    miners.sort()
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-2].hash)) ** 2) % len(miners)
    while True:
        bl = block.Block(miners[i][1], [miners[i][2]], [0.4, 0.3, 0.3], bch, [], [], miners[i][3])
        if bl.powhash < miners[i][0]:
            break
        else:
            i += 1
            if i == len(miners):
                 i = 0
    b.creators.append(miners[i])
    b.proportions.append(0.4)
    b.update()
    return b


def pos_mine(b, bch):
    """Proofs-of-stake mining"""
    miners = []
    for tnx in bch[-1].txs:
        if 'mining' in tnx.outs:
            miners.append([tnx.outns[tnx.outs.index('mining')], tnx.author])
    miners.sort()
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-3].hash)) ** 2) % len(miners)
    b.creators.append(miners[i])
    b.proportions.append(0.3)
    b.update()
    return b

def poc_mine(b, bch):
    """Proofs-of-capacity mining"""
    bindex = bch.index(b)
    miners = bch[bindex-1].pocminers
    miners.sort()
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-4].hash)) ** 2) % len(miners)
    miner = miners[i]
    b.creators.append(miner[1])
    b.proportions.append(0.3)
    b.update()
    return b


def mine(b, bch):
    # todo: write mining.mine()
    pos_mine(b, bch)
    return b


def validate(b, bch):
    """Checks is block mined"""
    # todo: write mining.validate()
    p = 0
    for prop in b.proportions:
        p += prop
    if p != block.minerfee:
        return False
    index = bch.index(b)
    posminers = []
    for tnx in bch[index-1].txs:
        if 'mining' in tnx.outs:
            posminers.append([tnx.outns[tnx.outs.index('mining')], tnx.author])
    bminers = set()
    try:
        bminers.add(posminers[(int(bch[index-1].txs[-1].hash) % len(posminers)) ** 0.5])
    except ZeroDivisionError:
        pass
    return True

    if int(b.h) >= b.n:
        return False
    ns = [b.n]
    # PoC, proportions checking, ns finding
    # warning: thing about what to do when some ns are equal
    if not b.n == max(ns):
        return False
    if not bminers == set(b.miners):
        return False
    return True

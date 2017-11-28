import block
import time
import cryptogr as cg


proofs_of_work_coef = 1
proofs_of_stake_coef = 1
proofs_of_capacity_coef = 1
#todo: write mining

def pow_mine(b, n, t):
    """proofs-of-work mining"""
    for i in range(t):
        b.timestamp = time.time()
        b.n = i
        b.update()
        if int(b.h) < n:
            return b
    b.update()
    return b


def pos_mine(b, bch):
    """Proofs-of-stake mining"""
    miners = []
    for tnx in bch[-1].txs:
        if 'mining' in tnx.outs:
            miners.append([tnx.outns[tnx.outs.index('mining')], tnx.author])
    miners.sort()
    i = (int(bch[-1].txs[-1].hash) % len(miners)) ** 0.5
    b.creators.append(miners[i])
    b.update()
    return b

def poc_mine(b, bch):
    """Proofs-of-capacity mining"""
    bindex = bch.index(b)
    miners = bch[bindex-1].pocminers
    miners.sort()
    i = (int(bch[-1].txs[-1].hash) % len(miners)) ** 0.5
    miner = miners[i]
    b.creators.append(miner[1])
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
    bminers.append(posminers[(int(bch[index-1].txs[-1].hash) % len(posminers)) ** 0.5])

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

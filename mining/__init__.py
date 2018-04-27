"""
This file contains functions for mining.
HODL has 4 ways of mining:
pow_mining: classical mining like in Bitcoin (proofs-of-work)
pos_mining: proofs-of-stake
pok_mining: miner stores smart contracts' data there is not only one miner, everybody who stores it becomes HODL
(proofs-of-keeping). It is the base for decentralized data storage.
poc_mining: miner calculates what smart contracts need (proofs-of-calcing). It is the base for dezentralized computing
in HODL.
"""
import block
import time
import cryptogr as cg


pow_max = 1000000000000000000000000000000000000
pos_min = 0.05
pok_total = 100000
poc_total = 100000
miningprice = [500, 0.05]


class TooLessTxsError(Exception):
    pass


class NoValidMinersError(Exception):
    pass


def is_pow_miner_valid(bch, miner):
    return True


def mining_delta_t(bch_len):
    return int(((0.005*bch_len)**0.95)/30+5)


def pow_mining(bch, b):
    """Proof-of-work new block processing
    miner:
    [hash, n, miner's address, timestamp]"""
    lb = bch[-1]
    miners = lb.powminers
    miners.sort()
    try:
        i = ((int(lb.txs[-1].hash) + int(lb.txs[-3].hash)) % int(len(miners) ** 0.5)) ** 2
    except IndexError:
        raise TooLessTxsError
    i1 = i
    while True:
        bl = block.Block(miners[i][1], [miners[i][2]], bch, [], [], miners[i][3])
        if int(bl.calc_pow_hash()) == miners[i][0] <= pow_max:
            print('i37', i)
            break
        else:
            miners.remove(miners[i])
            if i == i1:
                raise NoValidMinersError
            if i == len(bch):
                 i = i - len(bch) + 1
    b.n = miners[i][1]
    b.pow_timestamp = miners[i][3]
    b.timestamp = int(time.time())
    b.creators = [miners[i][2]]
    b.txs[0].outs.append(miners[i][2])
    b.update()
    return b


def pow_validate(bch, num):
    miners = bch[num - 1].powminers
    miners.sort(reverse=True)
    if len(miners) == 0:
        raise NoValidMinersError
    i = ((int(bch[num - 1].txs[num - 1].hash) + int(bch[num - 1].txs[-3].hash)) % int(len(miners) ** 0.5)) ** 2
    i1 = i
    bl = block.Block(miners[i][1], [miners[i][2]], bch, [], [], miners[i][3])
    while True:
        bl = block.Block(miners[i][1], [miners[i][2]], bch, [], [], miners[i][3])
        bl.prevhash = bch[i-1].h
        if int(bl.calc_pow_hash()) <= miners[i][0] <= pow_max:
            break
        else:
            miners.remove(miners[i])
            if i == i1:
                raise NoValidMinersError
            if i == len(bch):
                i = i - len(bch) + 1
    if not miners[i][2] == bch[num].creators[0] or not bch[num].pow_timestamp == miners[i][3] or not bch[num].n == miners[i][1]:
        print('block pow mining wrong.', not miners[i][2] == bch[num].creators[0], not bch[num].pow_timestamp == miners[i][3], not bch[num].n == miners[i][1], hash(miners[i][2])%100, hash(bch[num].creators[0])%100, bch[num].pow_timestamp, miners[i][3], bch[num].n, miners[i][1], i)
        return False
    return True


def pos_mining(b, bch):
    """Proof-of-stake new block processing"""
    miners = []
    for tnx in bch[-1].txs:
        if 'mining' in tnx.outs:
            miners.append([tnx.outns[tnx.outs.index('mining')], tnx.author])
    miners.sort(reverse=True)
    if len(miners) == 0:
        raise NoValidMinersError
    try:
        i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-4].hash)) % int(len(miners) ** 0.5)) ** 2
    except IndexError:
        raise TooLessTxsError
    if miners[i][0] >= pos_min:
        b.creators.append(miners[i][1])
    else:
        if miners[0][0] >= pos_min:
            b.creators.append(miners[i][1])
        else:
            raise NoValidMinersError
    b.txs[0].outs.append(miners[i][1])
    b.update()
    return b


def pos_validate(bch, i):
    b = bch[i]
    miners = []
    for tnx in bch[i-1].txs:
        if 'mining' in tnx.outs:
            miners.append([tnx.outns[tnx.outs.index('mining')], tnx.author])
    miners.sort()
    if len(miners) == 0:
        raise NoValidMinersError
    try:
        i = ((int(bch[i-1].txs[-1].hash) + int(bch[i-1].txs[-4].hash)) % int(len(miners) ** 0.5)) ** 2
    except IndexError:
        raise TooLessTxsError
    if miners[i][0] >= pos_min:
        if miners[i][1] == b.creators[1]:
            return True
    else:
        if miners[0][0] >= pos_min:
            if miners[0][1] == b.creators[1]:
                return True
        else:
            raise NoValidMinersError


def pok_mining(b, bch):
    """Proof-of-keeping new block processing"""
    tnx = block.Transaction()
    outs = []
    outns = []
    for bl in bch:
        for sc in bl.contracts:
            sc.calc_awards()
            for w in sc.awards.keys():
                if sc.awards[w][1] > bch[-1].timestamp:
                    outs.append(w)
                    outns.append(sc.awards[w][0])
    s = 0
    for n in outns:
        s += n
    for i in range(len(outns)):
        outns[i] = outns[i] * s / pok_total
    tnx.gen('mining', 'mining', outs, outns, [len(bch), len(b.txs)], 'mining', 'mining')
    b.txs.append(tnx)
    return b


def pok_validate(bch, n):
    outs = []
    outns = []
    for bl in bch:
        for sc in bl.contracts:
            sc.calc_awards(bch)
            for w in sc.awards.keys():
                if bch[n].timestamp > sc.awards[w][1] > bch[n - 1].timestamp:
                    outs.append(w)
                    outns.append(sc.awards[w][0])
    print('pok_validate. outns:', outns)
    s = 0
    for n in outns:
        s += n
    for i in range(len(outns)):
        outns[i] = outns[i] * s / pok_total
    print('pok_validate. total outns:', outns)
    if not (outs == bch[n].txs[1].outs and outns == bch[n].txs[1].outns):
        print('block pok mining wrong.', outns, bch[n].txs[1].outns, outs == bch[n].txs[1].outs)
        return False
    return True


def poc_mining(b, bch):
    """Proof-of-calcing new block processing"""
    return b


def poc_validate(bch, n):
    return True


def validate(bch, i=-1):
    """Checks is block mined"""
    # todo: write mining.validate()
    powv = pow_validate(bch, i)
    posv = pos_validate(bch, i)
    pokv = pok_validate(bch, i)
    pocv = poc_validate(bch, i)
    print(powv, posv, pokv, pocv)
    return all([powv, posv, pokv, pocv])


def mine(bch):
    """Creates new block"""
    b = block.Block()
    b.txs[0] = block.Transaction()
    b.txs[0].gen('mining', 'mining', [], miningprice, (len(bch), 0), 'mining', 'mining')
    b = pow_mining(bch, b)
    b = pos_mining(b, bch)
    b = pok_mining(b, bch)
    b = poc_mining(b, bch)
    b.prevhash = bch[-1].h
    b.calc_pow_hash()
    b.update()
    return b


def pow_mine(bch, nmax, myaddr):
    n = 0
    while True:
        t = int(time.time())
        bl = block.Block(n, [myaddr], bch, [], [], t)
        if int(bl.calc_pow_hash()) < nmax:
            break
        else:
            n += 1
    return n, t, int(bl.calc_pow_hash())

import block
import time
import cryptogr as cg


pow_max = 1000000000000000000000000000000000000
pos_min = 0.005
miningprice = [0.4, 0.3, 0.3]


class TooLessTxsError(Exception):
    pass


class NoValidMinersError(Exception):
    pass


def is_pow_miner_valid(bch, miner):
    return True


def mining_delta_t(bch_len):
    return int(((0.005*bch_len)**0.95)/30+5)


def pow_mining(bch, b):
    """Proof-of-work new block processing"""
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
    b.timestamp = miners[i][3]
    b.creators = [miners[i][2]]
    b.update()
    return b


def pow_validate(bch, num):
    miners = bch[num - 1].powminers
    miners.sort(reverse=True)
    i = ((int(bch[num - 1].txs[num - 1].hash) + int(bch[num - 1].txs[-3].hash)) % int(len(miners) ** 0.5)) ** 2
    i1 = i
    bl = block.Block(miners[i][1], [miners[i][2]], bch, [], [], miners[i][3])
    while True:
        bl = block.Block(miners[i][1], [miners[i][2]], bch, [], [], miners[i][3])
        bl.prevhash = bch[i-1].h
        if int(bl.calc_pow_hash()) <= miners[i][0] <= pow_max:
            print('i167', i)
            break
        else:
            miners.remove(miners[i])
            if i == i1:
                raise NoValidMinersError
            if i == len(bch):
                i = i - len(bch) + 1
    if not miners[i][2] == bch[num].creators[0] or not bch[num].timestamp == miners[i][3] or not bch[num].n == miners[i][1]:
        print(hash(miners[i][2])%100, hash(bch[num].creators[0])%100, bch[num].timestamp, miners[i][3], bch[num].n, miners[i][1], i)
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
    tnx.gen('mining', outs, outns, (len(bch), len(b)), 'mining', 'mining')
    b.txs.append(tnx)
    return b


def pok_validate(bch, n):
    return True


def poc_mining(b, bch):
    """Proof-of-calcing new block processing"""
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


def validate(bch, i=-1):
    """Checks is block mined"""
    # todo: write mining.validate()
    return all([pow_validate(bch, i), pos_validate(bch, i), pok_validate(bch, i), poc_validate(bch, i)])


def mine(bch):
    b = block.Block()
    b = pow_mining(bch, b)
    b = pos_mining(b, bch)
    b = pok_mining(b, bch)
    b = poc_mining(b, bch)
    b.txs[0].outns = miningprice
    return b

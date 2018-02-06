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

def mine(bch):
    b = block.Block()
    b = pow_mining(bch, b)
    b = pos_mining(b, bch)
    b = poc_mining(b, bch)
    b.txs[0].outns = miningprice
    return b


def pow_mining(bch, b):
    """proofs-of-work mining"""
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


def pos_mining(b, bch):
    """Proofs-of-stake mining"""
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

def poc_mining(b, bch):
    """Proofs-of-capacity mining"""
    # miner[0] - n, miner[1] - miner's public key, miner[2] - xs miner has calculated
    miners = bch[-1].pocminers
    if len(miners) == 0:
        raise NoValidMinersError
    for i in range(len(miners)):
        miners[i] = [len(miners[i][2]) * 20 + miners[i][0]] + miners[i]
    miners.sort()
    try:
        i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-2].hash)) % int(len(miners) ** 0.5)) ** 2
    except IndexError:
        raise TooLessTxsError
    i1 = i
    miner = miners[i]
    y = [((int(bch[-1].txs[-1].hash) * k + k) ** k) % miner[1] for k in range(100)]
    v = True
    while v:
        for x, k in miner[3]:
            print(86, k, x, (int(cg.h(str(x + len(bch)))) + int(cg.h(str(miner[2])))) % miner[1], y[k], len(bch), miner[1])
            if (int(cg.h(str(x+len(bch)))) + int(cg.h(str(miner[2])))) % miner[1] != y[k]:
                break
        else:
            v = False
        if v:
            miners.remove(miner)
            if i == i1:
                raise NoValidMinersError
            if i == len(bch):
                i = i - len(bch) + 1
            miner = miners[i]
            y = [((int(bch[-1].txs[-1].hash) * i + i) ** i) % miner[1] for i in range(100)]
    b.creators.append(miner[2])
    b.update()
    return b

def poc_mine(n, bch, myaddr):
    xs = []
    file = open('poc_mining.txt', 'w')
    file.close()
    file = open('poc_mining.txt', 'a')
    f = []
    y = [((int(bch[-1].txs[-1].hash) * k + k) ** k) % n for k in range(100)]
    for i in range(n):
        f.append(str((int(cg.h(str(i+len(bch)))) + int(cg.h(str(myaddr)))) % n)+'\n')
    file.writelines(f)
    file.close()
    with open('poc_mining.txt', 'r') as file:
        f = [int(i) for i in file.readlines()]
    for i in range(len(y)):
        try:
            xs.append([f.index(y[i]), i])
        except:
            pass
    return xs


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
    return all([validate_pow(bch, i), validate_pos(bch, i), validate_poc(bch, i)])
    """
    vw = validate_pow(bch, i)
    if not vw:
        return False
    vs = validate_pos(bch, i)
    if not vs:
        return False
    vc = validate_poc(bch, i)
    if not vc:
        return False
    return True
    """

def validate_pow(bch, num):
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

def validate_poc(bch, n):
    bl = bch[n]
    miners = bch[n-1].pocminers
    if n < 0:
        n = len(bch) + n
    for i in range(len(miners)):
        miners[i] = [len(miners[i][2]) * 20 + miners[i][0]] + miners[i]
    miners.sort()
    print(bch[n-1].txs)
    i = ((int(bch[n-1].txs[-1].hash) + int(bch[n-1].txs[-2].hash)) % int(len(miners) ** 0.5)) ** 2
    i1 = i
    miner = miners[i]
    y = [((int(bch[n-1].txs[-1].hash) * k + k) ** k) % miner[1] for k in range(100)]
    v = True
    while v:
        for p in miners[i][3]:
            x = p[0]
            k = p[1]
            if (int(cg.h(str(x + n))) + int(cg.h(str(miner[2])))) % miner[1] != y[k]:
                print(i, k, x, (int(cg.h(str(x + n))) + int(cg.h(str(miner[2])))) % miner[1], y[k], n, miner[1])
                break
        else:
            v = False
        if v:
            miners.remove(miner)
            if i == i1:
                raise NoValidMinersError
            if i == len(bch):
                i = i - len(bch) + 1
            miner = miners[i]
            y = [((int(bch[n-1].txs[-1].hash) * i + i) ** i) % miner[1] for i in range(100)]
    if not miners[i][2] == bl.creators[1]:
        return False
    return True

def validate_pos(bch, i):
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


def mining_delta_t(bch_len):
    return int(((0.005*bch_len)**0.95)/30+5)

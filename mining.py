import block
import time
import cryptogr as cg


pow_max = 1000000000000000000000000000000000000


class TooLessTxsError(Exception):
    pass

class NoValidMinersError(Exception):
    pass

def mine(bch):
    b = block.Block()
    b = pow_mining(bch, b)
    b = pos_mining(b, bch)
    b = poc_mining(b, bch)
    return b


def pow_mining(bch, b):
    """proofs-of-work mining"""
    miners = bch[-1].powminers
    miners.sort(reverse=True)
    print(len(miners), 'miners', miners)
    try:
        i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-3].hash)) % int(len(miners) ** 0.5)) ** 2
    except IndexError:
        raise TooLessTxsError
    while True:
        print(i)
        bl = block.Block(miners[i][1], [miners[i][2]], bch, [], [], miners[i][3])
        if int(bl.calc_pow_hash()) <= miners[i][0] <= pow_max:
            break
        else:
            i -= 1
            if len(miners) == 1:
                raise NoValidMinersError
            if i < 0:
                 i = len(miners) - 1
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
    miners.sort()
    if len(miners) == 0:
        raise NoValidMinersError
    try:
        i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-4].hash)) % int(len(miners) ** 0.5)) ** 2
    except IndexError:
        raise TooLessTxsError
    b.creators.append(miners[i])
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
            if (int(cg.h(str(x+len(bch)))) + int(cg.h(str(miner[2])))) % miner[1] != y[k]:
                break
        else:
            v = False
        if v:
            i -= 1
            if i == -1:
                i = len(miners) - 1
            if i == i1:
                raise NoValidMinersError
            miner = miners[i]
            y = [((int(bch[-1].txs[-1].hash) * i + i) ** i) % miner[1] for i in range(100)]
    b.creators.append(miner[1])
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
        t = time.time()
        bl = block.Block(n, [myaddr], bch, [], [], t)
        if int(bl.calc_pow_hash()) < nmax:
            break
        else:
            n += 1
    return n, t, bl.calc_pow_hash()


def validate(bch, i=-1):
    """Checks is block mined"""
    # todo: write mining.validate()
    return validate_pow(bch, i) and validate_pos(bch, i) and validate_poc(bch, i)

def validate_pow(bch, i):
    miners = bch[i].powminers
    miners.sort(reverse=True)
    i = ((int(bch[i-1].txs[i - 1].hash) + int(bch[i - 1].txs[-3].hash)) % int(len(miners) ** 0.5)) ** 2
    while True:
        bl = block.Block(miners[i][1], [miners[i][2]], bch, [], [], miners[i][3])
        if int(bl.calc_pow_hash()) <= miners[i][0] <= pow_max:
            break
        else:
            i -= 1
            if i < 0:
                 i = len(miners) - 1
    if not miners[i][2] == bch[i].creators[0] or not bch[i].timestamp == miners[i][3] or not bch[i].n == miners[i][1]:
        return False
    return True

def validate_poc(bch, i):
    b = bch[i]
    return True

def validate_pos(bch, i):
    b = bch[i]
    return True


def mining_delta_t(bch_len):
    return int(((0.001*bch_len)**1.15)/100+5)

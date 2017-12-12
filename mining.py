import block
import time
import cryptogr as cg


#todo: write mining

def pow_mining(bch, b):
    """proofs-of-work mining"""
    miners = bch[-1].powminers
    miners.sort(reversed=True)
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-2].hash)) ** 2) % len(miners)
    while True:
        bl = block.Block(miners[i][1], [miners[i][2]], [0.4, 0.3, 0.3], bch, [], [], miners[i][3])
        if int(bl.powhash) < miners[i][0]:
            break
        else:
            i += 1
            if i == len(miners):
                 i = 0
    b.creators.append(miners[i])
    b.proportions.append(0.4)
    b.update()
    return b


def pos_mining(b, bch):
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

def poc_mining(b, bch):
    """Proofs-of-capacity mining"""
    bindex = bch.index(b)
    miners = bch[bindex-1].pocminers
    miners.sort()
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-4].hash)) ** 2) % len(miners)
    miner = miners[i]
    y = [(int(bch[-1].txs[-1].hash) ** k) % miner[0] for k in range(1000)]
    # miner[0] - number of values miner has calculated, miner[1] - miner's public key, miner[2] - xs miner has calculated
    while v:
        v = True
        for k in range(1000):
            if int(cg.h(str(miner[2][k] + len(bch)) + str(miner[1]))) == y[k]:
                v = False
                break
        if v:
            i += 1
            miner = miners[i]
            y = [(int(bch[-1].txs[-1].hash) ** i) % miner[0] for i in range(1000)]
    b.creators.append(miner[1])
    b.proportions.append(0.3)
    b.update()
    return b

def poc_mine(n, bch, myaddr):
    xs = []
    f = open('poc_mine.txt', 'a')
    y = [(int(bch[-1].txs[-1].hash) ** k) % n for k in range(1)]
    for i in range(n):
        f.write(cg.h(str(i+len(bch)) + str(myaddr)))
    f.close()
    file = open('poc_mine.txt', 'r')
    f = [int(i) for i in list(file)]
    file.close()
    print(y)
    for i in range(1):
        try:
            xs.append(f.index(y[i]))
        except:
            return xs, False
    return xs, True


def pow_mine(bch, nmax, myaddr):
    n = 0
    while True:
        t = time.time()
        bl = block.Block(n, [myaddr], [0.4, 0.3, 0.3], bch, [], [], t)
        if int(bl.powhash) < nmax:
            break
        else:
            n += 1
    return n, t


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

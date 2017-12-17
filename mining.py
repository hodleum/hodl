import block
import time
import cryptogr as cg


#todo: write mining

def pow_mining(bch, b):
    """proofs-of-work mining"""
    miners = bch[-1].powminers
    miners.sort(reversed=True)
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-3].hash)) % (len(miners) ** 0.5)) ** 2
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
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-4].hash)) % (len(miners) ** 0.5)) ** 2
    b.creators.append(miners[i])
    b.proportions.append(0.3)
    b.update()
    return b

def poc_mining(b, bch):
    """Proofs-of-capacity mining"""
    # miner[0] - n, miner[1] - miner's public key, miner[2] - xs miner has calculated
    bindex = bch.index(b)
    miners = bch[bindex-1].pocminers
    for i in range(miners):
        miners[i] = [miners[i][2] * 20 + miners[i][0]] + miners[i]
    miners.sort()
    i = ((int(bch[-1].txs[-1].hash) + int(bch[-1].txs[-2].hash)) % (len(miners) ** 0.5)) ** 2
    miner = miners[i]
    y = [((int(bch[-1].txs[-1].hash) * k + k) ** k) % miner[0] for k in range(10)]
    while v:
        v = True
        for k in range(100):
            if (int(cg.h(str(i+len(bch)))) + int(cg.h(str(miner[2])))) % miner[1] == y[k]:
                v = False
                break
        if v:
            i += 1
            miner = miners[i]
            y = [((int(bch[-1].txs[-1].hash) * i + i) ** i) % miner[1] for i in range(10)]
    b.creators.append(miner[1])
    b.proportions.append(0.3)
    b.update()
    return b

def poc_mine(n, bch, myaddr):
    xs = []
    file = open('poc_mining.txt', 'w')
    file.close()
    file = open('poc_mining.txt', 'a')
    f = []
    y = [((int(bch[-1].txs[-1].hash) * k + k) ** k) % n for k in range(100)]
    t = time.time()
    for i in range(n):
        f.append(str((int(cg.h(str(i+len(bch)))) + int(cg.h(str(myaddr)))) % n)+'\n')
    file.writelines(f)
    file.close()
    print(76, time.time()-t)
    with open('poc_mining.txt', 'r') as file:
        f = [int(i) for i in file.readlines()]
    t = time.time()
    for i in range(len(y)):
        print(i, t - time.time())
        try:
            xs.append(f.index(y[i]))
        except:
            pass
        t = time.time()
    print(t - time.time())
    return xs


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

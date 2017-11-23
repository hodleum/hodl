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
        if b.h < n:
            return block
    return b


def pos_mine(block, bch):
    """Proofs-of-stake mining"""
    miners = []
    for b in bch:
        for tnx in b.txs:
            if 'mining' in tnx.outs:
                miners.append([tnx.outns[tnx.outs.index('mining')], tnx.author])
    miners.sort()
    i = int(cg.h(bch[-1].txs[-1])) % len(miners)    # todo: добавить функцию, через которую будет проходить эта инфа
    block.creators.append(miners[i])


def poc_mine(block):
    """Proofs-of-capacity mining"""
    pass


def mine(block):
    # todo: write mining.mine()
    b = block
    return b


def validate(b):
    """Checks is block mined"""
    # todo: write mining.validate()
    p = 0
    for prop in b.proportions:
        p += prop
    if p != block.minerfee:
        return False
    # осталось чуть-чуть
    return True

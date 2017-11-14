import block
import time


proofs_of_work_coef = 1
proofs_of_stake_coef = 1
proofs_of_capacity_coef = 1
#todo: write mining

def pow_mine(block, n, t):
    """proofs-of-work mining"""
    b = block
    for i in range(t):
        b.timestamp = time.time()
        b.n = i
        b.update()
        if b.h < n:
            return block
    return b


def pos_mine(block, pubkey):
    """Proofs-of-stake mining"""
    pass


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

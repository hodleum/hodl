import block


proofs_of_work_coef = 1
proofs_of_stake_coef = 1
proofs_of_capacity_coef = 1


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

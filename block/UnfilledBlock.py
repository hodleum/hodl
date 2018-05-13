import json
import cryptogr as cg
from block.Transaction import *


class UnfilledBlock:
    """
    UnfilledBlock
    It is class for part of the block, for example this block can store not all transactions,
    not all smart contracts etc
    """
    def __init__(self, n=0, creators=[], bch=[], txs=[], contracts=[], pow_timestamp='now', t='now'):
        self.n = n
        self.prevhash = get_prevhash(bch, creators)
        self.timestamp = get_timestamp(t)
        self.pow_timestamp = pow_timestamp
        tnx0 = Transaction()
        tnx0.gen('mining', [['nothing']], creators, mining.miningprice, (len(bch), 0), b'mining', '', self.pow_timestamp)
        self.txs = [tnx0] + txs
        self.contracts = contracts
        self.creators = creators
        self.powminers = []
        self.powhash = 0
        self.powhash = self.calc_pow_hash()
        self.update()

    def update(self):
        """Updates hash"""
        h = ''.join([str(self.prevhash)] + [str(self.powhash)] + [str(t.hash) for t in self.txs] +
                    [str(sc) for sc in self.contracts] + [str(e) for e in self.powminers])
        self.h = cg.h(str(h))

    def __str__(self):
        s = ''
        return s

    @classmethod
    def from_json(cls, s):
        self = cls()
        return self

    def calc_pow_hash(self):
        try:
            h = ''.join([str(self.pow_timestamp), str(self.n), self.creators[0]])
        except IndexError:
            h = ''.join([str(self.pow_timestamp), str(self.n)])
        return cg.h(str(h))

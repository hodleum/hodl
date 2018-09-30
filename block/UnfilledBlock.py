import json
import cryptogr as cg
import json
from block.Transaction import *


class UnfilledBlock:
    """
    UnfilledBlock
    It is class for part of the block, for example this block can store not all transactions,
    not all smart contracts etc
    Unfilled block shouldn't be last, because hash cannot be recalculated.
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
        self.is_unfilled = True
        self.powhash = 0
        self.powhash = self.calc_pow_hash()
        self.update()

    def update(self):
        """Updates hash. Pass because only unfilled block is only for unchangeable blocks"""
        pass

    def __str__(self):
        s = ''
        # todo
        return s

    @classmethod
    def from_json(cls, s):
        self = cls()
        # todo
        return self

    def calc_pow_hash(self):
        try:
            h = ''.join([str(self.pow_timestamp), str(self.n), self.creators[0]])
        except IndexError:
            h = ''.join([str(self.pow_timestamp), str(self.n)])
        return cg.h(str(h))

    def is_valid(self):
        # todo
        return True

    def get_tnx(self, ind, sync_get):
        """
        Get transaction by index
        :param ind: index of transaction to get
        :type ind: list
        :param sync_get: function than gets object (block, transaction, smart contract) from network
        :type sync_get: function
        :return: Transaction
        """
        for tnx in self.txs:
            if tnx.index[1] == ind:
                return tnx
        else:
            return sync_get(json.dumps([{'type': 'tnx', 'index': ind}]))

    def get_sc(self, ind, sync_get):
        """
        Get smart contract by index
        :param ind: index of smart contract to get
        :type ind: list
        :param sync_get: function than gets object (block, transaction, smart contract) from network
        :type sync_get: function
        :return: SmartContract
        """
        for sc in self.contracts:
            if sc.index[1] == ind:
                return sc
        else:
            return sync_get(json.dumps([{'type': 'sc', 'index': ind}]))

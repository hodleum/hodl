import time
import json
import logging as log
from block.Transaction import Transaction
from block.sc import SmartContract
import cryptogr as cg
import mining
from block.Fixer import BlockFixer
from mining.pool import Miners
from block.constants import block_time


def get_timestamp(t):
    return int(time.time()) if t == 'now' else int(t)


def get_prevhash(bch, creators):
    try:
        if creators and bch[-1].h:
            return bch[-1].h
        else:
            return '0'
    except AttributeError:
        return '0'


class Block:
    """Class for blocks.
    To convert block to string, use str(block)
    To convert string to block, use Block.from_json(string)"""

    def __init__(self, creators=(), bch=(), txs=(), contracts=(), t='now'):
        self.prevhash = get_prevhash(bch, creators)
        self.timestamp = get_timestamp(t)
        self.is_unfilled = False
        tnx0 = Transaction()
        tnx0.gen('mining', [['nothing']], creators, mining.miningprice, (len(bch), 0), 'mining', '',
                 self.timestamp)
        self.txs = [tnx0] + list(txs)
        self.contracts = contracts
        self.miners = Miners()
        self.fixer = None
        self.h = None

        self.update()

    def __str__(self):
        """
        Encodes block to str using JSON
        :return:block, converted to str
        """
        return json.dumps(([str(t) for t in self.txs], self.timestamp, self.prevhash,
                           [str(c) for c in self.contracts], str(self.fixer) if self.fixer else None, str(self.miners)))

    @classmethod
    def from_json(cls, s):
        """
        Decodes block from str using JSON
        :param s: string - encoded block
        :return: Block
        """
        self = cls()
        s = json.loads(s)
        self.txs = []
        self.contracts = []
        for t in s[0]:
            self.txs.append(Transaction.from_json(t))
        for c in s[3]:
            sc = SmartContract.from_json(c)
            self.contracts.append(sc)
        self.timestamp, self.prevhash, self.fixer, self.miners = s[1], s[2], s[4], s[5]
        if self.fixer:
            self.fixer = BlockFixer.from_json(self.fixer)
        self.miners = Miners.from_json(self.miners)
        self.update()
        return self

    def append(self, txn):
        """
        Adds txn to block
        :param txn: Transaction to add to block
        """
        self.txs.append(txn)  # Add transaction to transaction list
        self.update()  # update hash

    def update(self):
        """Updates hash"""
        self.sort()
        h = json.dumps((str(self.prevhash), [str(t.hash) for t in self.txs],
                    [str(sc) for sc in self.contracts], hash(self.miners)))
        self.h = cg.h(str(h))

    def is_valid(self, bch):
        """
        Validate block
        :param bch: Blockchain
        :return: validness (bool)
        """
        self.sort()
        i = bch.index(self)
        v = True
        if i != 0:
            n = 0
            for o in self.txs[0].outns:
                n += o
            if self.txs[0].outns != mining.miningprice:
                log.warning('not all money in first tnx')
                return False
            for t in self.txs[2:]:
                if not t.is_valid(bch):
                    log.warning("tnx {} isn't valid".format(str(t.index)))
                    return False
            if i != 0:
                if not mining.validate(bch, i):
                    log.warning('not valid mined block. i:', i)
                    return False
            if i != 0:
                if self.prevhash != bch[i - 1].h:
                    log.warning('prevhash not valid. i:', i)
                    return False
            else:
                pass
        else:
            pass    # todo: write first block processing - hash comparation
        return v

    def __eq__(self, other):
        """
        compare blocks
        :param other: Block
        :return: is equal
        """
        return self.h == other.h

    def is_full(self):
        """is block full"""
        return time.time() > block_time + self.timestamp  # int(((0.005*bch_len)**0.95)/30+5)

    def sort(self):
        """Sort transactions in block"""
        t0 = self.txs[0]
        ts = [[int(tnx.timestamp), int(tnx.hash), tnx] for tnx in self.txs[1:]]
        ts.sort()
        self.txs = [t0] + [t[2] for t in ts]
        for i in range(len(self.txs)):
            self.txs[i].index[1] = i

    def make_unfilled(self, important_wallets=()):
        txs = [self.txs[0]]
        for tnx in self.txs:
            if tnx.author in important_wallets or not set(important_wallets).isdisjoint(set(tnx.outs)):
                txs.append(tnx)

    def rev(self, bch):
        self.sort()
        for i in range(len(self.txs)):
            if not self.txs[i].is_valid(bch):
                self.txs.pop(i)
        for i in range(len(self.contracts)):
            if not self.contracts[i].is_valid(bch):
                self.contracts.pop(i)
        self.sort()
        self.update()

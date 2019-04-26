"""
Module describing block - an item of blockchain
"""
import time
import json
import logging as log
from .Transaction import Transaction
from .sc import SmartContract
from hodl import cryptogr as cg
from . import mining
from .Fixer import BlockFixer
from .mining.pool import Miners
from .constants import block_time
from .sc.task import Task


def get_timestamp(t):
    return int(time.time()) if t == 'now' else int(t)


def get_prevhash(bch):
    try:
        if len(bch):
            return bch[-1].h
        else:
            return '0'
    except (AttributeError, IndexError):
        return '0'


class Block:
    """
    Class for blocks.
    To convert block to string, use str(block)
    To convert string to block, use Block.from_json(string)
    """

    def __init__(self, txs=(), t='now', bch=None, index=None):
        super().__setattr__('_index', index)
        super().__setattr__('_bch', bch)
        self.prevhash = get_prevhash(bch) if bch else None
        self.timestamp = get_timestamp(t)
        self.txs = list(txs)
        self.miners = Miners()
        self.fixer = None
        self.h = None
        self.sc_tasks = []   # completed tasks add here
        self.update(False)

    def append(self, txn):
        """
        Adds txn to block

        :param txn: Transaction to add to block
        """
        self.txs.append(txn)  # Add transaction to transaction list
        self.update()  # update hash

    def update(self, sort=True):
        """
        Updates hash
        """
        if sort:
            self.sort()
        h = json.dumps((str(self.prevhash), [str(t.hash) for t in self.txs],
                        hash(self.miners), [str(task) for task in self.sc_tasks]))
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

    def is_full(self):
        """is block full"""
        return time.time() > block_time + self.timestamp  # int(((0.005*bch_len)**0.95)/30+5)

    def sort(self):
        """Sort transactions in block"""
        ts = [[int(tnx.timestamp), int(tnx.hash), tnx] for tnx in self.txs]
        ts.sort()
        self.txs = [t[2] for t in ts]
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
        self.sort()
        self.update()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if self._index:
            self._bch[self._index] = self

    def __eq__(self, other):
        """
        Compare blocks

        :param other: Block
        :return: is equal
        """
        return self.h == other.h

    def __str__(self):
        """
        Encodes block to str using JSON

        :return:block, converted to str
        """
        return json.dumps(([str(t) for t in self.txs], self.timestamp, self.prevhash,
                           str(self.fixer) if self.fixer else None, str(self.miners),
                           [str(task) for task in self.sc_tasks]))

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
        self.timestamp, self.prevhash, self.fixer, self.miners = s[1], s[2], s[3], s[4]
        if self.fixer:
            self.fixer = BlockFixer.from_json(self.fixer)
        self.miners = Miners.from_json(self.miners)
        self.sc_tasks = [Task.from_json(task) for task in s[5]]
        self.update()
        return self

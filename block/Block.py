import time
import json
from block.Transaction import *
from block.Smart_contract import *
import mining

maxblocksize = 4000000


def get_timestamp(t):
    return int(time.time()) if t == 'now' else int(t)


def get_prevhash(bch, creators):
    try:
        if creators:
            return bch[-1].h
        else:
            return '0'
    except:
        return '0'


class Block:
    """Class for blocks.
    To convert block to string, use str(block)
    To convert string to block, use Block.from_json(string)"""
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

    def __str__(self):
        """Encodes block to str using JSON"""
        return json.dumps(([str(t) for t in self.txs], self.n, self.timestamp, self.prevhash, self.creators,
                           [str(c) for c in self.contracts], self.powminers, self.pow_timestamp))

    @classmethod
    def from_json(cls, s):
        """Decodes block from str using JSON"""
        self = cls()
        s = json.loads(s)
        self.txs = []
        self.contracts = []
        for t in s[0]:
            self.txs.append(Transaction.from_json(t))
        for c in s[5]:
            sc = Smart_contract.from_json(c)
            self.contracts.append(sc)
        self.n, self.timestamp, self.prevhash, self.creators, self.powminers, self.pow_timestamp = s[1], s[2], s[3], \
                                                                                                   s[4], s[6], s[7]
        self.powhash = self.calc_pow_hash()
        self.update()
        return self

    def new_transaction(self, author, froms, outs, outns, sign='signing', privkey=''):
        """Creates new transaction and adds it to the chain"""
        tnx = Transaction()
        tnx.gen(author, froms, outs, outns, (len(self)-1, len(self[-1].txs)), sign, privkey)
        self.append(tnx)

    def append(self, txn):
        """Adds txn to block"""
        self.txs.append(txn)  # добавляем транзакцию в список транзакций
        self.update()  # обновляем хэш

    def update(self):
        """Updates hash"""
        self.sort()
        h = ''.join([str(self.prevhash)] + [str(self.powhash)] + [str(t.hash) for t in self.txs] +
                    [str(sc) for sc in self.contracts] + [str(e) for e in self.powminers])
        self.h = cg.h(str(h))

    def is_valid(self, bch):
        """Returns validness of block"""
        i = bch.index(self)
        v = True
        if i != 0:
            if self.txs[0].froms != 'mining' or self.txs[0].author != 'mining' \
                    or self.txs[0].outs != self.creators:
                print('invalid first tnx')
                return False
            n = 0
            for o in self.txs[0].outns:
                n += o
            if self.txs[0].outns != mining.miningprice:
                print('not all money in first tnx')
                return False
            for t in self.txs[2:]:
                if not t.is_valid(bch):
                    print('tnx isnt valid')
                    return False
            if i != 0:
                if not mining.validate(bch, i):
                    print('not valid mined block. i:', i)
                    return False
            if i != 0:
                if self.prevhash == bch[i - 1].h:
                    print('prevhash not valid. i:', i)
                    return False
            else:
                pass
        # todo: write first block processing
        return v

    def __eq__(self, other):
        return self.h == other.h

    def is_full(self):
        """is block full"""
        return len(str(self)) >= maxblocksize

    def calc_pow_hash(self):
        try:
            h = ''.join([str(self.pow_timestamp), str(self.n), self.creators[0]])
        except IndexError:
            h = ''.join([str(self.pow_timestamp), str(self.n)])
        return cg.h(str(h))

    def sort(self):
        """Sort transactions in block"""
        t0 = self.txs[0]
        ts = [[int(tnx.timestamp), int(tnx.hash), tnx] for tnx in self.txs[1:]]
        ts.sort()
        self.txs = [t0] + [t[2] for t in ts]
        for i in range(len(self.txs)):
            self.txs[i].index[1] = i
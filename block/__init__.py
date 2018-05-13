"""
Classes:
Blockchain:
Class for storing blockchain. Connects to the sqlite3 database
Main methods:
    new_block - creates new block
    new_transaction - creates new transaction
    new_sc - creates new smart contract
Block:
Class for storing block
Transaction:
Class for storing transaction.
Smart_contract:
Class for storing smart contract.

Some abbreviations:
bch - blockchain
tnx - transaction
sc - smart contract(DApp)
"""
import sqlite3
from block.Smart_contract import *
from block.Transaction import *
from block.Block import Block
from block.UnfilledBlock import UnfilledBlock
from block.SimpleSC import SimpleSC

minerfee = 1


class Blockchain:
    """Class for blockchain"""
    def __init__(self, filename='bch.db', m='w'):
        self.f = filename
        if m != 'ro':
            self.conn = sqlite3.connect(filename)
        else:
            self.conn = sqlite3.connect('file' + filename + '?mode=ro', uri=True)
        self.c = self.conn.cursor()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS blocks
                     (ind integer, block text)''')
        self.conn.commit()

    def __getitem__(self, item):
        if type(item) == slice:
            l = []
            if item.step is None:
                step = 1
            else:
                step = item.step
            for i in range([item.start, len(self)][item.stop is not None], [item.stop, len(self)][item.stop is None],
                           [step, len(self)][item.stop is not None]):
                l.append(self[i])
            return l
        if item < 0:
            item += len(self)
        self.c.execute("SELECT * FROM blocks WHERE ind=?", (item, ))
        s = self.c.fetchone()[1]
        return Block.from_json(s)

    def append(self, block):
        self.c.execute("INSERT INTO blocks VALUES (?, ?)", (len(self), str(block)))
        self.conn.commit()

    def index(self, block):
        """Finds block in chain by hash"""
        for i in range(len(self)):
            if self[i].h == block.h:
                return i

    def money(self, wallet):
        """Counts money on wallet"""
        money = 0
        for i in range(len(self)):  # every tnx in every block
            for tnx in self[i].txs:
                outs, outns = rm_dubl_from_outs(tnx.outs, tnx.outns)
                l = zip(outs, outns, range(len(outns)))
                for w, n, j in l:
                    if (w == wallet or w == self.pubkey_by_nick(wallet)) and not tnx.spent(self)[j] and 'mining' not in tnx.outs:
                        money += n
        return money

    def new_block(self, creators, txs=[]):
        """Creates the new block and adds it to chain"""
        b = Block(0, creators, self, txs)
        self.append(b)

    def is_valid(self):
        """Returns validness of the whole chain"""
        for i, b in enumerate(self[1:]):
            if not b.is_valid(self):
                print('block not valid:', i + 1)
                return False
        return True

    def new_transaction(self, author, froms, outs, outns, sign='signing', privkey=''):
        """Creates new transaction and adds it to the chain"""
        tnx = Transaction()
        tnx.gen(author, froms, outs, outns, (len(self)-1, len(self[-1].txs)), sign, privkey)
        b = self[-1]
        b.append(tnx)
        self[-1] = b

    def __str__(self):
        """Encodes blockchain to str"""
        return json.dumps([str(e) for e in self])

    def from_json(self, s):
        """Decodes blockchain from str"""
        bs = json.loads(s)
        for b in bs:
            block = Block()
            block.from_json(b)
            self.append(block)

    def new_sc(self, text, author, author_priv, memsize):
        """creates new smart contract and adds it to the chain"""
        b = self[-1]
        sc = Smart_contract(text, author, [len(self) - 1, len(b.contracts)], memsize=memsize)
        sc.sign_sc(author_priv)
        b.contracts.append(sc)
        self[-1] = b

    def __len__(self):
        self.c.execute("SELECT ind FROM blocks")
        return len(self.c.fetchall())

    def __iter__(self):
        self.current = -1
        return self

    def __next__(self):
        self.current += 1
        if self.current != len(self):
            return self[self.current]
        else:
            raise StopIteration

    def __setitem__(self, key, value):
        if key < 0:
            key += len(self)
        self.c.execute("""UPDATE blocks SET block = ? WHERE ind = ?""", (str(value), key))
        self.conn.commit()

    def add_miner(self, miner):
        """add proof-of-work miner
        miner = [hash, n, address, t]"""
        b = self[-1]
        b.powminers.append(miner)
        self[-1] = b

    def clean(self):
        self.c.execute('''DELETE FROM blocks''')
        self.conn.commit()

    def add_sc(self, sc):
        b = self[-1]
        b.contracts.append(sc)
        self[-1] = b

    def close(self):
        self.conn.commit()
        self.conn.close()

    def commit(self):
        self.close()
        self.conn = sqlite3.connect(self.f)
        self.c = self.conn.cursor()

    def __repr__(self):
        return str([[len(b.txs), len(b.contracts)] for b in self])

    def pubkey_by_nick(self, nick):
        if nick.startswith('-----BEGIN PUBLIC KEY-----'):
            if nick.endswith('-----END PUBLIC KEY-----'):
                return nick
            else:
                return nick.split('-----END PUBLIC KEY-----')[0]+'-----END PUBLIC KEY-----'
        else:
            o = None
            for i in range(len(self)):
                for tnx in self[i].txs:
                    if tnx.author.endswith(nick+';'):
                        o = nick.split('-----END PUBLIC KEY-----')[0]+'-----END PUBLIC KEY-----'
        # todo
        return

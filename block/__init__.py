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
from block.sc import *
from block.Transaction import *
from block.Block import Block
from block.UnfilledBlock import UnfilledBlock


# todo: blockchain freeze before new block
# todo: transaction and smart contract limit or hash mining, remove smart contract's comission
# todo: smart contracts and SC messages connected to transaction


class Blockchain:
    """Class for blockchain"""
    def __init__(self, filename='bch.db', m='w'):
        self.f = filename
        if m != 'ro':
            self.conn = sqlite3.connect('db/' + filename)
        else:
            self.conn = sqlite3.connect('db/'+filename + '?mode=ro', uri=True)
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

    def tnxiter(self, maxn=('l', 'l'), fr=(0, 0)):
        maxn = list(maxn)
        if maxn[0] == 'l':
            maxn[0] = len(self)
        if maxn[1] == 'l':
            maxn[1] = len(self[-1].txs)
        if maxn[0] < 0:
            maxn[0] = len(self) + maxn[0]
        if maxn[1] < 0:
            maxn[1] = len(self[-1].txs) + maxn[1]
        if fr[0] > maxn[0]:
            return
        elif fr[0] == maxn[0]:
            for tnx in self[fr[0]].txs[fr[1]:maxn[1]]:
                yield tnx
        else:
            for tnx in self[fr[0]].txs[fr[1]:]:
                yield tnx
            for i in range(fr[0] + 1, maxn[0] - 1):
                for tnx in self[i].txs:
                    yield tnx
            for tnx in self[maxn[0]-1].txs[:maxn[1]]:
                yield tnx

    def get_sc(self, smartcontract):
        """
        Get smart contract by index
        :param smartcontract: index
        :type smartcontract: str
        :return: Smart contract
        :type: SmartContrct
        """
        smartcontract = smartcontract[:-1].split('[')[1].replace(' ', '').split(',')
        smartcontract = [int(smartcontract[0]), int(smartcontract[1])]

    def verify_sc_sign(self, smartcontract, sign):
        """
        Verify smart contract's sign
        :param smartcontract: smart contract's index
        :type smartcontract: str
        :param sign: sign
        :type sign: str
        :return: validness
        :type: bool
        """
        return self.get_sc(smartcontract).validate_sign(sign)

    def money(self, wallet, at=('l', 'l')):
        """Counts money on wallet"""
        at = list(at)
        money = 0
        for tnx in self.tnxiter(maxn=at):  # every tnx in every block
            outs, outns = rm_dubl_from_outs(tnx.outs, tnx.outns)
            l = zip([self.pubkey_by_nick(o) for o in outs], outns, range(len(outns)))
            for w, n, j in l:
                if (w == wallet or w == self.pubkey_by_nick(wallet)) and not tnx.spent(self)[j] \
                        and 'mining' not in tnx.outs:
                    money += n
        return round(money, 10)

    def new_block(self, creators, txs=tuple()):
        """Creates the new block and adds it to chain"""
        b = Block(0, creators, self, txs)
        self.append(b)

    def is_valid(self):
        """Returns validness of the whole chain"""
        for i in range(1, len(self)):
            if not self[i].is_unfilled:
                if not self[i].is_valid(self):
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
        sc = SmartContract(text, author, [len(self) - 1, len(b.contracts)], memsize=memsize)
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

    def get_block(self, i, sync_get):
        """
        Return full block (In local blockchain might be only unfilled copy of block i (UnfilledBlock),
        then get full block from other peer)
        :param i: block's index
        :type i: int
        :param sync_get: function than gets object (block, transaction, smart contract) from network
        :type sync_get: function
        :return: Block
        """
        if not self[i].is_unfilled:
            return self[i]
        else:
            return sync_get(json.dumps([{'type': 'block', 'index': i}]))

    def add_miner(self, miner):
        """add proof-of-work miner
        miner = [hash, n, address, t]"""
        b = self[-1]
        b.powminers.append(miner)
        self[-1] = b

    def clean(self):
        """
        Delete all blocks from blockchain
        """
        self.c.execute('''DELETE FROM blocks''')
        self.conn.commit()

    def add_sc(self, sc):
        """
        Add smart contract
        :param sc:
        :return:
        """
        b = self[-1]
        b.contracts.append(sc)
        self[-1] = b

    def commit(self):
        self.close()
        self.conn = sqlite3.connect(self.f)
        self.c = self.conn.cursor()

    def pubkey_by_nick(self, nick, maxn=('l', 'l')):
        """
        Nicks can be used in transactions. Nicks can be defined in transaction with author=pubkey;nick;
        Nick can be transfered in transaction with autor=pubkey;nick;new pubkey;
        :param nick: str: pubkey, nick or nick definition
        :param maxn: tuple: maximum index or ('l', 'l') for entire blockchain
        :return: str: pubkey
        """
        if ';' not in nick and '[' not in nick and len(nick) > 20:
            return nick
        elif '[' in nick and ';' not in nick:
            return nick
        if nick.count(';') >= 2:
            return nick.split(';')[0]
        o = None
        for tnx in self.tnxiter(maxn=maxn):
            if tnx.author.endswith(nick + ';'):
                o = tnx.author.split(';')[0]
            elif ';' in tnx.author:
                if tnx.author.count(';') == 3 and tnx.author.split(';')[1] == nick:
                    o = tnx.author.split(';')[1]
        return o

    def has_traffic_rest(self, user, time_to, price, mined_hash=None):
        """
        HODL has no commission, so, to avoid spam, user has limit of actions in proportion to his balance.
        Next actions must be mined by this user. (todo)
        :param user: author of action to confirm
        :type user: str
        :param time_to: time of action
        :type time_to: float
        :param price: price of the action
        :type price: float
        :param mined_hash: mined hash for mined actions
        :type mined_hash: int
        :return: validness of the action
        :rtype: bool
        """
        m = self.money(user, time_to)
        # todo: count all action prices
        return True

    def close(self):
        """Close connection to database"""
        self.conn.commit()
        self.conn.close()

    def __repr__(self):
        return str([[len(b.txs), len(b.contracts)] for b in self])

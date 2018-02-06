import cryptogr as cg
import time
from itertools import chain
import json
import mining
import sqlite3
import os

minerfee = 1
txs_in_block = 50
maxblocksize = 4000000
sc_base_mem = 10000000
sc_base_code_size = 5000000
sc_memprice = 10**(1/10)
sc_max_code_size = 1000000000
sc_code_price = 10**(1/6)
sc_price = 0.01


class Blockchain:
    """Class for blockchain"""
    def __init__(self):
        self.conn = sqlite3.connect('bch.db')
        self.c = self.conn.cursor()
        try:
            self.c.execute('''CREATE TABLE blocks
                         (ind integer, block text)''')
            self.conn.commit()
        except:
            pass

    def __getitem__(self, item):
        if item < 0:
            item += len(self)
        self.c.execute("SELECT * FROM blocks WHERE ind=" + str(item))
        s = self.c.fetchone()[1]
        return Block.from_json(s)

    def append(self, block):
        self.c.execute("INSERT INTO blocks VALUES ({}, {})".format(str(len(self)), "'" + str(block) + "'"))
        self.conn.commit()

    def index(self, block):
        for i in range(len(self)):
            if self[i].h == block.h:
                return i

    def money(self, wallet):
        """Counts money on wallet"""
        money = 0
        for bl in self:  # перебираем все транзакции в каждом блоке
            for tnx in bl.txs:
                l = zip(tnx.outs, tnx.outns, range(len(tnx.outns)))
                for w, n, i in l:
                    if w == wallet and not tnx.spent(self)[i]:
                        money += n
        return money

    def new_block(self, creators, txs=[]):
        """Creates the new block and adds it to chain"""
        b = Block(0, creators, self, txs)
        self.append(b)

    def is_valid(self):
        """Returns validness of the whole chain"""
        for b in self:
            if not b.is_valid(self):
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

    def new_sc(self, text, author):
        """creates new smart contract and adds it to the chain"""
        b = self[-1]
        b.contracts.append(Smart_contract(text, author, [len(b), len(self) - 1]))
        self[-1] = b

    def __eq__(self, other):
        """equal function"""
        return self.__dict__ == other.__dict__

    def __len__(self):
        self.c.execute("SELECT ind FROM blocks")
        return len(self.c.fetchall())

    def __iter__(self):
        self.current = -1
        return self

    def __next__(self):
        self.current += 1
        if not self.current <= len(self):
            return self[self.current]
        else:
            raise StopIteration

    def __setitem__(self, key, value):
        if key < 0:
            key += len(self)
        self.c.execute("UPDATE blocks SET block = '{}' WHERE ind = {}".format(str(value), str(key)))

    def add_miner(self, miner, type='pow'):
        if type == 'pow':
            b = self[-1]
            b.powminers.append(miner)
            self[-1] = b
        elif type == 'poc':
            b = self[-1]
            b.pocminers.append(miner)
            self[-1] = b

    def clean(self):
        self.c.execute('''DELETE FROM blocks''')
        self.conn.commit()

def get_timestamp(t):
    return int(time.time()) if t=='now' else int(t)

def get_prevhash(bch, creators):
    try:
        if creators:
            return bch[-1].h
        else:
            return '0'
    except:
        return '0'


class Block:
    """Class for blocks"""
    def __init__(self, n=0, creators=[], bch=Blockchain(), txs=[], contracts=[], t='now'):
        self.n = n
        self.prevhash = get_prevhash(bch, creators)
        self.timestamp = get_timestamp(t);
        tnx0 = Transaction()
        tnx0.gen('mining', [['nothing']], creators, [0.4, 0.3, 0.3], (len(bch), 0), b'mining', '', self.timestamp)
        self.txs = [tnx0] + txs
        self.contracts = contracts
        self.creators = creators
        self.pocminers = []
        self.powminers = []
        self.powhash = 0
        self.powhash = self.calc_pow_hash()
        self.update()

    def __str__(self):
        """Encodes block to str using JSON"""
        return json.dumps(([str(t) for t in self.txs], self.n, self.timestamp, self.prevhash, self.creators,
                           [str(c) for c in self.contracts], self.pocminers, self.powminers))

    @classmethod
    def from_json(cls, s):
        """Decodes block from str using JSON"""
        self = cls()
        s = json.loads(s)
        self.txs = []
        for t in s[0]:
            tnx = Transaction()
            tnx.from_json(t)
            self.txs.append(tnx)
        for c in s[5]:
            sc = Smart_contract()
            sc.from_json(c)
            self.contracts.append(sc)
        self.n, self.timestamp, self.prevhash, self.creators, self.pocminers, self.powminers = s[1], s[2], s[3], s[4], s[6], s[7]
        self.powhash = self.calc_pow_hash()
        self.update()
        return self

    def append(self, txn):
        """Adds txn to block"""
        self.txs.append(txn)  # добавляем транзакцию в список транзакций
        self.update()  # обновляем хэш

    def update(self):
        """Updates hash"""
        self.sort()
        h = ''.join([str(self.prevhash)] + [str(self.powhash)] + [str(t.hash) for t in self.txs] +
                    [str(sc) for sc in self.contracts] + [str(e) for e in self.powminers] +
                    [str(e) for e in self.pocminers])
        self.h = cg.h(str(h))

    def is_valid(self, bch):
        """Returns validness of block"""
        i = bch.index(self)
        v = True
        if i != 0:
            if self.txs[0].froms != [['nothing']] or self.txs[0].author != 'mining' \
                    or self.txs[0].outs != self.creators:
                print('invalid first tnx')
                return False
            n = 0
            for o in self.txs[0].outns:
                n += o
            if n != minerfee:
                print('not all money in first tnx')
                return False
            for t in self.txs[1:]:
                if not t.is_valid(bch):
                    print('tnx isnt valid')
                    return False
            if not i == 0:
                if not mining.validate(bch, i):
                    return False
            if i != 0:
                v = self.prevhash == bch[i - 1].h
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
            h = ''.join([str(self.timestamp), str(self.n), self.creators[0]])
        except IndexError:
            h = ''.join([str(self.timestamp), str(self.n)])
        return cg.h(str(h))

    def sort(self):
        t0 = self.txs[0]
        ts = [[int(tnx.timestamp), int(tnx.hash), tnx] for tnx in self.txs[1:]]
        ts.sort()
        self.txs = [t0] + [t[2] for t in ts]
        for i in range(len(self.txs)):
            self.txs[i].index[1] = i


def is_first_tnx_valid(tnx, bch):
    if tnx.froms != [['nothing']] or tnx.author != 'mining' \
            or tnx.outs != bch[tnx.index[0]].creators or tnx.outns != mining.miningprice:
        return False
    else:
        return True

def is_tnx_money_valid(self, bch):
    inp = 0
    for t in self.froms:  # Проверка наличия требуемых денег в транзакциях-донорах
        try:
            tnx = bch[int(t[0])].txs[int(t[1])]
            if not tnx.is_valid:
                print(self.index, 'is not valid: from is not valid')
                return False
            if tnx.spent(bch, [self.index])[tnx.outs.index(self.author)]:
                print(self.index, 'is not valid: from is not valid')
                return False
            inp = inp + tnx.outns[tnx.outs.index(self.author)]
        except:
            print(self.index, 'is not valid: exception')
            return False
    o = 0
    for n in self.outns:  # all money must be spent
        if n < 0:
            return False
        o = o + n
    if not o == inp:
        print(self.index, 'is not valid: not all money')
        return False
    return True

def sign_tnx(self, sign, privkey, t):
    if sign == 'signing':
        self.sign = cg.sign(self.hash, privkey)
    else:
        self.sign = sign
    return self.sign


class Transaction:
    """Class for transaction"""
    # форма для передачи транзакций строкой(разделитель - русское а):
    # author + а + str(froms)+ а + str(outs) + а + str(outns) + а + str(time)+ а + sign
    def __str__(self):
        """Encodes transaction to str using JSON"""
        return json.dumps((self.author, self.froms, self.outs, self.outns, self.index, str(list(self.sign)), self.timestamp))

    def from_json(self, s):
        """Decodes transacion from str using JSON"""
        s = json.loads(s)
        self.gen(s[0], s[1], s[2], s[3], list(s[4]), bytearray(eval(s[5])), '', s[6])
        self.update()

    def gen(self, author, froms, outs, outns, index, sign='signing', privkey='', t='now'):
        self.froms = froms  # номера транзакций([номер блока в котором лежит нужная транзакция,
        # номер нужной транзакции в блоке),
        # из которых эта берет деньги
        self.outs = outs  # номера кошельков-адресатов
        self.outns = outns  # количество денег на каждый кошелек-адресат
        self.author = author  # тот, кто проводит транзакцию
        self.index = list(index)
        self.timestamp = time.time() if sign == 'signing' else t
        self.update()
        self.sign = sign_tnx(self, sign, privkey, t)
        self.update()

    def is_valid(self, bch):
        """Returns validness of transaction.
        Checks:
        is sign valid
        are all money spent"""
        if self.index[1]==0:
            is_first_tnx_valid(self, bch)
        if not self.author[0:2] == 'sc':
            if not cg.verify_sign(self.sign, self.hash, self.author):
                print(self.index, 'is not valid: sign is wrong')
                return False
        else:
            scind = [int(self.author[2:].split(';')[0]), int(self.author[2:].split(';')[1])]
            sc = bch[scind[0]].contracts[scind[1]]
            for tnx in sc.txs:
                if self.index == tnx.index:
                    break
            else:
                return False
        is_tnx_money_valid(self, bch)
        self.update()
        return True


    def __eq__(self, other):
        return self.hash == other.hash

    def spent(self, bch, exc=[]):
        """Is transaction used by other transaction"""
        spent = [False] * len(self.outs)
        for block in bch:  # перебираем все транзакции в каждом блоке
            for tnx in block.txs[1:]:
                if list(self.index) in tnx.froms and not 'mining' in tnx.outs and not tnx.index in exc:
                    spent[self.outs.index(tnx.author)] = True
        return spent

    def update(self):
        x = ''.join(chain(str(self.author), str(self.index), [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns], str(self.timestamp)))
        self.hash = cg.h(str(x))
        return self.hash


class Smart_contract:
    def __init__(self, code, author, index, prolongable=False, computing=False, tasks=[], mem_copies=3, calc_repeats=3):
        self.code = code
        self.author = author
        self.index = index
        self.memory = []
        self.msgs = []
        self.prolongable = prolongable
        self.timestamp = time.time()
        self.computing = True
        self.tasks = tasks
        self.membs = []
        self.memsize = sc_base_mem
        self.codesize = sc_base_code_size
        self.txs = []
        self.mem_copies = mem_copies
        self.calc_repeats = calc_repeats


    def execute(self):
        """smart contract's execution"""
        file = open('tmp/{}.py'.format(str(self.index)), 'w')
        file.writelines(self.code)
        file.close()
        file = open('tmp/{}.mem'.format(str(self.index)), 'w')
        file.writelines([str(mem) for mem in list(self.memory)])
        file.close()
        file = open('tmp/{}.msgs'.format(str(self.index)), 'w')
        file.writelines([str(mem) for mem in list(self.msgs)])
        file.close()
        os.system('docker run -v "$(pwd)"/tmp:/home/hodl/tmp -v "$(pwd)"/bch.db:/home/hodl/bch.db:ro scrun_container python3 /home/hodl/tmp/{}.py'.format(str(self.index)))
        file = open('tmp/{}.mem'.format(str(self.index)), 'r')
        self.memory = [str(mem) for mem in file.readlines()]
        file.close()
        file = open('tmp/{}.txs'.format(str(self.index)), 'r')
        self.txs.append([Transaction.from_json(tnxstr) for tnxstr in file.readlines()])
        file.close()

    def __str__(self):
        """Encodes contract to str"""
        return json.dumps((self.code, self.author, self.index, self.prolongable, self.computing, self.tasks,
                           self.mem_copies, self.calc_repeats, self.msgs, self.membs, self.memsize,
                           self.codesize, self.timestamp))

    @classmethod
    def from_json(cls, s):
        """Decodes contract from str"""
        self = cls(*json.loads(s)[0:8])
        self.msgs, self.membs, self.memsize, self.codesize, self.timestamp = json.loads[7:]
        return self

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def is_valid(self, bch):
        if self.codesize > sc_max_code_size:
            return False
        pr = sc_price
        if self.memsize > sc_base_mem or self.codesize > sc_base_code_size:
            pr += ((self.memsize - sc_base_mem) * sc_memprice * (time.time()//2592000)) + (self.codesize - sc_base_code_size) * sc_code_price
        payed = 0
        for b in bch:
             for tnx in b.txs:
                 if tnx.author == self.author and str(self.index) + 'payment' in tnx.outs:
                     payed += tnx.outns[tnx.outs.index(str(self.index) + 'payment')]
        if not payed >= pr:
            return False

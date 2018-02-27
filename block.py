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
    def __init__(self, filename='bch.db'):
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS blocks
                     (ind integer, block text)''')
        self.conn.commit()

    def __getitem__(self, item):
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
        try:
            return self[self.current]
        except TypeError:
            raise StopIteration

    def __setitem__(self, key, value):
        if key < 0:
            key += len(self)
        self.c.execute("""UPDATE blocks SET block = ? WHERE ind = ?""", (str(value), key))

    def add_miner(self, miner):
        """adds proof-of-work miner"""
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
    """Class for blocks"""
    def __init__(self, n=0, creators=[], bch=Blockchain(), txs=[], contracts=[], pow_timestamp='now', t='now'):
        self.n = n
        self.prevhash = get_prevhash(bch, creators)
        self.timestamp = get_timestamp(t)
        self.pow_timestamp = pow_timestamp
        tnx0 = Transaction()
        tnx0.gen('mining', [['nothing']], creators, [0.4, 0.3, 0.3], (len(bch), 0), b'mining', '', self.pow_timestamp)
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
        for t in s[0]:
            tnx = Transaction()
            tnx.from_json(t)
            self.txs.append(tnx)
        for c in s[5]:
            sc = Smart_contract.from_json(c)
            self.contracts.append(sc)
        self.n, self.timestamp, self.prevhash, self.creators, self.powminers, self.pow_timestamp = s[1], s[2], s[3], s[4], s[6], s[7]
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
                    [str(sc) for sc in self.contracts] + [str(e) for e in self.powminers])
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
            h = ''.join([str(self.pow_timestamp), str(self.n), self.creators[0]])
        except IndexError:
            h = ''.join([str(self.pow_timestamp), str(self.n)])
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
    for t in self.froms:  # how much money are available
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
                if list(self.index) in tnx.froms and 'mining' not in tnx.outs and not tnx.index in exc:
                    spent[self.outs.index(tnx.author)] = True
        return spent

    def update(self):
        x = ''.join(chain(str(self.author), str(self.index), [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns], str(self.timestamp)))
        self.hash = cg.h(str(x))
        return self.hash


class Smart_contract:
    def __init__(self, code, author, index, computing=False, tasks=[], mem_copies=3, calc_repeats=3,
                 memsize=sc_base_mem, codesize=sc_base_code_size):
        self.code = code
        self.author = author
        self.index = index
        self.memory = []
        self.msgs = []  # [[message func, message args(the first is message's sender), str(list(sender's sign))]]
        self.timestamp = time.time()
        self.computing = computing
        self.tasks = tasks  # [[command, {miner:[[acceptions or declinations(a/d, sign, address)], time solved]},
        # repeats, award, done]]
        self.mempeers = []
        self.memsize = memsize
        self.codesize = codesize
        self.txs = []
        self.mem_copies = mem_copies
        self.calc_repeats = calc_repeats
        self.awards = {}
        self.sign = ''

    def sign_sc(self, privkey):
        self.sign = cg.sign(json.dumps((self.code, str(self.author), self.index, self.computing, self.tasks,
                           self.mem_copies, self.calc_repeats, self.msgs, self.mempeers, self.memsize,
                           self.codesize, self.timestamp)), privkey)

    def execute(self, func='', args=[]):
        """smart contract's execution"""
        os.mkdir('tmp')
        file = open('tmp/main.py', 'w')
        if func == '':
            file.writelines(['from sc import *\n'])
        else:
            file.writelines(['from sc import *\n', 'import json\n', 'args = json.loads({})\n'.format(json.dumps(args)),
                             '{}(*args)\n'.format(func)])
        file.close()
        file = open('tmp/sc.py', 'w')
        file.writelines(self.code)
        file.close()
        file = open('tmp/sc.mem', 'w')
        file.writelines([str(mem) for mem in list(self.memory)])
        file.close()
        file = open('tmp/sc.msgs', 'w')
        file.writelines([str(mem) for mem in list(self.msgs)])
        file.close()
        file = open('tmp/sc.tasks', 'w')
        file.writelines([json.dumps(task) for task in list(self.tasks)])
        file.close()
        open('tmp/sc.txs', 'w').close()
        os.system('docker run -v "$(pwd)"/tmp:/home/hodl -v "$(pwd)"/bch.db:/home/hodl/bch.db:ro scrun_container python3 /home/hodl/main.py')
        file = open('tmp/sc.mem', 'r')
        self.memory = [str(mem) for mem in file.readlines()]
        file.close()
        file = open('tmp/sc.tasks', 'r')
        self.tasks = [json.loads(task) for task in file.readlines()]
        file.close()
        file = open('tmp/sc.txs', 'r')
        self.txs.append([Transaction.from_json(tnxstr) for tnxstr in file.readlines()])
        file.close()
        os.system('rm -rf tmp')

        # todo: sc tnx

    def __str__(self):
        """Encodes contract to str"""
        json.dumps((str(list(self.sign))))
        json.dumps((self.author))
        json.dumps((self.code))
        json.dumps((self.timestamp))
        json.dumps((self.codesize))
        json.dumps((self.memsize))
        json.dumps((self.mem_copies))
        json.dumps((self.calc_repeats))
        json.dumps((self.msgs))
        json.dumps((self.mempeers))
        json.dumps((self.tasks))
        return json.dumps((self.code, self.author, self.index, self.computing, self.tasks,
                           self.mem_copies, self.calc_repeats, self.msgs, self.mempeers, self.memsize,
                           self.codesize, self.timestamp, str(list(self.sign))))

    @classmethod
    def from_json(cls, s):
        """Decodes contract from str"""
        self = cls(*json.loads(s)[0:7])
        self.msgs, self.membs, self.memsize, self.codesize, self.timestamp, self.sign = json.loads(s)[7:]
        return self

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def is_valid(self, bch):
        if self.codesize > sc_max_code_size:
            return False
        pr = sc_price
        if self.memsize > sc_base_mem or self.codesize > sc_base_code_size:
            pr += ((self.memsize - sc_base_mem) * sc_memprice) + ((self.codesize - sc_base_code_size) * sc_code_price)
        payed = 0
        for b in bch:
            for tnx in b.txs:
                if tnx.author == self.author and str(self.index) + 'payment' in tnx.outs:
                    payed += tnx.outns[tnx.outs.index(str(self.index) + 'payment')]
        if not payed >= pr:
            return False
        if not cg.verify_sign(self.sign, json.dumps((self.code, str(self.author), self.index, self.computing, self.tasks,
                           self.mem_copies, self.calc_repeats, self.msgs, self.mempeers, self.memsize,
                           self.codesize, self.timestamp)), self.author):
            return False
        return True

    def calc_awards(self):
        self.awards = {}
        for task in self.tasks:
            for w in task[1].keys():
                accepts = 0
                for a in task[1][w][0]:
                    if a[0] == 'a':
                        accepts += 1
                if accepts < (0.7 * task[2]):
                    if w in self.awards.keys():
                        self.awards[w].append([task[3], task[1][w][1]])
                    else:
                        self.awards[w] = [task[3]]

    def handle_messages(self):
        for mess in self.msgs:
            if mess[-1] == False:
                if cg.verify_sign(mess[2], json.dumps([mess[0], mess[1]]), mess[1][0]):
                    self.execute(mess[0], mess[1])

    def __eq__(self, other):
        v = True
        if self.__dict__.keys() != other.__dict__.keys():
            print('sc.__eq__ keys not equal', self.__dict__.keys(), other.__dict__.keys())
            v = False
        for k in self.__dict__.keys():
            if self.__dict__[k] != other.__dict__[k]:
                print(k, self.__dict__[k], other.__dict__[k])
        return str(self) == str(other)

import cryptogr as cg
import time
from itertools import chain
import json
import mining

minerfee = 1
txs_in_block = 50
maxblocksize = 4000000

class Blockchain(list):
    """Class for blockchain"""
    def __add__(self, other):    # todo: дописать
        """Merges blockchains (consensus)"""
        if other.is_valid():
            if len(other) > len(self):
                self = other

    def money(self, wallet):
        """Counts money on wallet"""
        money = 0
        for block in self:  # перебираем все транзакции в каждом блоке
            for tnx in block.txs:
                for w, n, i in zip(tnx.outs, tnx.outns, range(len(tnx.outns))):
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
        self[-1].append(tnx)

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

    def new_sc(self, text, author, needsinf=False, payment_method='for execution', payment_opts={'for 1 execution': 1}):
        """creates new smart contract and adds it to the chain"""
        for i, block in enumerate(self):
            if not block.is_full():
                block.contracts.append(text, author, (i, len(block.contracts)), needsinf, payment_method, payment_opts)
                break

    def __eq__(self, other):
        """equal function"""
        return self.__dict__ == other.__dict__


class Block:
    """Class for blocks"""
    def __init__(self, n=0, creators=[], bch=Blockchain(), txs=[], contracts=[], t='now'):
        self.n = n
        try:
            self.prevhash = bch[-1].h
        except:
            self.prevhash = '0'
        if t == 'now':
            self.timestamp = int(time.time())
        else:
            self.timestamp = int(t)
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

    def from_json(self, s):
        """Decodes block from str using JSON"""
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

    def append(self, txn):
        """Adds txn to block"""
        self.txs.append(txn)  # добавляем транзакцию в список транзакций
        self.update()  # обновляем хэш

    def update(self):
        """Updates hash"""
        self.sort()
        h = ''.join([str(self.powhash)] + [str(t.hash) for t in self.txs] +
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
        return self.__dict__ == other.__dict__

    def is_full(self):
        """is block full"""
        return len(str(self)) >= maxblocksize

    def calc_pow_hash(self):
        h = ''.join([str(self.prevhash), str(self.timestamp), str(self.n)] + [str(e) for e in self.creators[:1]])
        return cg.h(str(h))

    def sort(self):
        t0 = self.txs[0]
        ts = [[int(tnx.timestamp), int(tnx.hash), tnx] for tnx in self.txs[1:]]
        ts.sort()
        self.txs = [t0] + [t[2] for t in ts]
        for i in range(len(self.txs)):
            self.txs[i].index[1] = i


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
        if t == 'now':
            self.timestamp = time.time()
        else:
            self.timestamp = t
        if sign == 'signing':  # транзакция может быть уже подписана,
            # или может создаваться новая транзакция с помощью Transaction().
            # Соответственно может быть нужна новая подпись.
            self.update()
            self.sign = cg.sign(self.hash, privkey)
        else:  # Если транзакция не проводится, а создается заново после передачи, то подпись уже известна
            self.sign = sign
            self.timestamp = t
        self.update()

    def is_valid(self, bch):
        """Returns validness of transaction.
        Checks:
        is sign valid
        are all money spent"""
        if self.index[1] == 0:
            if self.froms != [['nothing']] or self.author != 'mining' \
                    or self.outs != bch[self.index[0]].creators:
                return False
            else:
                return True
        if not self.author[0:2] == 'sc':
            if not cg.verify_sign(self.sign, self.hash, self.author):
                print(self.index, 'is not valid: sign is wrong')
                return False
        else:
            try:
                scind = [int(self.author[2:].split(';')[0]), int(self.author[2:].split(';')[1])]
                sc = bch[scind[0]].contracts[scind[1]]
                tnx_needed, tnx_created, froms, outs, outns = sc.execute()[1:]
                if tnx_needed:
                    selfind = froms.index(self.froms)
                    if not (tnx_created and outs[selfind] == self.outs and outns[selfind] == self.outns):
                        return False
                else:
                    print(self.index, 'is not valid: sc')
                    return False
            except:
                print(self.index, 'is not valid: exception')
                return False
        inp = 0
        for t in self.froms:  # Проверка наличия требуемых денег в транзакциях-донорах
            try:
                if t == ['nothing']:
                    if not (self.index[1] == 0 and self.outs[0] == bch[self.index[0]].creators and
                                    self.outns == [0.4, 0.3, 0.3]):
                        return False
                    inp = minerfee
                else:
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
            o = o + n
        if not o == inp:
            print(self.index, 'is not valid: not all money')
            return False
        x = ''.join(chain([str(self.sign), str(self.author), str(self.index)], [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns]))
        return True


    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def spent(self, bch, exc=[]):
        """Is transaction used by other transaction"""
        spent = [False] * len(self.outs)
        for block in bch:  # перебираем все транзакции в каждом блоке
            for tnx in block.txs:
                if list(self.index) in tnx.froms and not 'mining' in tnx.outs and not tnx.index in exc:
                    spent[self.outs.index(tnx.author)] = True
        return spent

    def update(self):
        x = ''.join(chain(str(self.author), str(self.index), [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns], str(self.timestamp)))
        self.hash = cg.h(str(x))
        return self.hash


class Smart_contract:
    # todo: дописать Smart_contract: добавить ограничения
    def __init__(self, text, author, index, needsinf=False, payment_method='for execution',
                 payment_opts={'for 1 execution': 1}):
        self.text = text
        self.author = author
        self.payment_method = payment_method
        self.index = index
        self.result = ''
        self.needsinf = needsinf
        self.payment_opts = payment_opts
        self.info = ''

    def execute(self, bch, inf=''):
        """smart contract's execution"""
        loc = {}
        loc['info'] = self.info
        if self.needsinf:
            exec(self.text, {'inf': str(inf)}, loc)
        else:
            exec(self.text, {}, loc)
        result = loc['result']
        tnx_needed = loc['tnx_needed']  # Smart contract can create transactions
        tnx_created = loc['tnx_created']
        froms = loc['froms']
        outs = loc['outs']
        outns = loc['outns']
        sc_needed = loc['sc_needed']  # Smart contract can create smart contracts
        sc_created = loc['sc_created']
        sc_text = loc['sc_text']
        sc_author = loc['sc_author']
        sc_payment_method = loc['sc_payment_method']
        sc_needsinf = loc['sc_needsinf']
        sc_payment_opts = loc['sc_payment_opts']
        self.info = str(loc['info'])
        # froms, outs, outns = params of transactions SC needs
        # If SC doesn't need a tnx, froms, outs, outns =[], [], []
        # SC can return result. It's needed for applications that use SCs
        if tnx_needed:
            for i in range(len(froms)):
                if not tnx_created[i]:
                    try:
                        bch.new_transaction('sc' + str(self.index[0]) + ';' + str(self.index[1]), froms[i], outs[i],
                                            outns[i],
                                            'sc' + str(self.index[0]) + ';' + str(self.index[1]),
                                            'sc' + str(self.index[0]) + ';' + str(self.index[1]))
                    except:
                        pass
        if sc_needed:
            for i in range(len(sc_created)):
                if not sc_created[i]:
                    try:
                        bch.new_sc(sc_text[i], sc_author[i], sc_needsinf[i], sc_payment_method[i],
                                   sc_payment_opts[i])
                    except:
                        pass
        self.result = result
        return result, tnx_needed, tnx_created, froms, outs, outns

    def __str__(self):
        """Encodes contract to str"""
        return json.dumps((self.text, self.author, self.index, self.needsinf, self.payment_method, self.payment_opts))

    def from_json(self, s):
        """Decodes contract from str"""
        self.__init__(*json.loads(s))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

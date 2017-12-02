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
                if wallet in tnx.outs and not tnx.spent(self)[tnx.outs.index(wallet)]:
                    money += tnx.outns[tnx.outs.index(wallet)]
        return money

    def new_block(self, creators, proportions, txs=[]):
        """Creates the new block and adds it to chain"""
        b = Block(0, creators, proportions, self, txs)
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
        for i, block in enumerate(self[1:]):
            if not block.is_full():
                tnx.gen(author, froms, outs, outns, (i, len(block.txs)), sign, privkey)
                block.append(tnx)
                break

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
    def __init__(self, n=0, creators=[], proportions=[], bch=Blockchain(), txs=[], contracts=[]):
        self.n = n
        try:
            self.prevhash = bch[-1].h
        except:
            self.prevhash = '0'
        self.timestamp = time.time()
        tnx0 = Transaction()
        tnx0.gen('mining', [['nothing']], creators, proportions, (len(bch), 0), b'mining')
        self.txs = [tnx0] + txs
        self.contracts = contracts
        self.creators = creators
        self.proportions = proportions
        self.pocminers = []
        self.update()

    def __str__(self):
        """Encodes block to str using JSON"""
        return json.dumps(([str(t) for t in self.txs], self.n, self.timestamp, self.prevhash, self.creators,
                           [str(c) for c in self.contracts], self.pocminers))

    def from_json(self, s):
        """Decodes block from str using JSON"""
        s = json.loads(s)
        for t in s[0]:
            tnx = Transaction()
            tnx.from_json(t)
            self.txs.append(tnx)
        for c in s[5]:
            sc = Smart_contract()
            sc.from_json(c)
            self.contracts.append(sc)
        self.n, self.timestamp, self.prevhash, self.creators, self.pocminers = s[1], s[2], s[3], s[4], s[5]
        self.update()

    def append(self, txn):
        """Adds txn to block"""
        self.txs.append(txn)  # добавляем транзакцию в список транзакций
        self.update()  # обновляем хэш

    def update(self):
        """Updates hash"""
        h = ''.join([str(self.prevhash), str(self.timestamp), str(self.n)] + [str(t.hash) for t in self.txs])
        self.h = cg.h(str(h))

    def is_valid(self, bch):
        """Returns validness of block"""
        h = str(bch.index(self)) + str(self.prevhash) + str(self.timestamp) + str(self.n)
        if self.txs[0].froms != [['nothing']] or self.txs[0].author != 'mining' \
                or self.txs[0].outs != [self.creators] \
                or self.txs[0].outns != minerfee:
            return False
        for t in self.txs[1:]:
            h = h + str(t.hash)
            if not t.is_valid(bch):
                return False
        if not mining.validate(self):
            return False
        v = cg.h(str(h)) == self.h and self.prevhash == bch[bch.index(self) - 1].h
        return v

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def is_full(self):
        """is block full"""
        return len(str(self)) >= maxblocksize


class Transaction:
    """Class for transaction"""
    # форма для передачи транзакций строкой(разделитель - русское а):
    # author + а + str(froms)+ а + str(outs) + а + str(outns) + а + str(time)+ а + sign
    def __str__(self):
        """Encodes transaction to str using JSON"""
        return json.dumps((self.author, self.froms, self.outs, self.outns, self.index, self.sign.decode('utf-8')))

    def from_json(self, s):
        """Decodes transacion from str using JSON"""
        s = json.loads(s)
        self.gen(s[0], s[1], s[2], s[3], s[4], s[5].encode('utf-8'))

    def gen(self, author, froms, outs, outns, index, sign='signing', privkey=''):
        self.froms = froms  # номера транзакций([номер блока в котором лежит нужная транзакция,
        # номер нужной транзакции в блоке),
        # из которых эта берет деньги
        self.outs = outs  # номера кошельков-адресатов
        self.outns = outns  # количество денег на каждый кошелек-адресат
        self.author = author  # тот, кто проводит транзакцию
        self.index = index
        if sign == 'signing':  # транзакция может быть уже подписана,
            # или может создаваться новая транзакция с помощью Transaction().
            # Соответственно может быть нужна новая подпись.
            self.sign = cg.sign(str(self.froms) + str(self.outs) + str(self.outns), privkey)
        else:  # Если транзакция не проводится, а создается заново после передачи, то подпись уже известна
            self.sign = sign
        x = ''.join(chain([str(self.sign), str(self.author), str(self.index)], [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns]))
        self.hash = cg.h(str(x))

    def is_valid(self, bch):
        """Returns validness of transaction.
        Checks:
        is sign valid
        are all money spent"""
        if not self.author[0:2] == 'sc':
            if not cg.verify_sign(self.sign, str(self.froms) + str(self.outs) + str(self.outns), self.author):
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
                print(self.index, 'is not valid: exception183')
                return False
        inp = 0
        for t in self.froms:  # Проверка наличия требуемых денег в транзакциях-донорах
            try:
                if t == ['nothing']:
                    if not (self.index[1] == 0 and self.outs[0] == bch[self.index[0]].creators and
                                    self.outns == bch[self.index[0]].proportions):
                        return False
                    inp = minerfee
                else:
                    tnx = bch[int(t[0])].txs[int(t[1])]
                    if not tnx.is_valid:
                        print(self.index, 'is not valid: from is not valid')
                        return False
                    if tnx.spent(bch)[tnx.outs.index(self.author)]:
                        print(self.index, 'is not valid: from is not valid')
                        return False
                    inp = inp + tnx.outns[tnx.outs.index(self.author)]
            except:
                print(self.index, 'is not valid: exception197')
                return False  # Если возникает какая-нибудь ошибка, то транзакция точно невалидная
        o = 0
        for n in self.outns:  # должны быть израсходованы все взятые деньги
            o = o + n
        if not o == inp:
            print(self.index, 'is not valid: not all money')
            return False
        x = ''.join(chain([str(self.sign), str(self.author), str(self.index)], [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns]))
        if not self.hash == cg.h(str(x)):
            print(self.index, 'is not valid: hash is not valid')
            return False
        return True


    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def spent(self, bch):
        """Is transaction used by other transaction"""
        spent = [False] * len(self.outs)
        for block in bch:  # перебираем все транзакции в каждом блоке
            for tnx in block.txs:
                if self.index in tnx.froms:
                    spent[self.outs.index(tnx.author)] = True
        return spent


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

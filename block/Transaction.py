import json
import cryptogr as cg
from itertools import chain
import time


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
    """Class for transaction.
    To create new transaction, use:
    tnx=Transaction()
    tnx.gen(parameters)"""
    # форма для передачи транзакций строкой(разделитель - русское а):
    # author + а + str(froms)+ а + str(outs) + а + str(outns) + а + str(time)+ а + sign
    def __str__(self):
        """Encodes transaction to str using JSON"""
        return json.dumps((self.author, self.froms, self.outs, self.outns, self.index,
                           str(list(self.sign)), self.timestamp))

    @classmethod
    def from_json(cls, s):
        """Decodes transacion from str using JSON"""
        s = json.loads(s)
        self = cls()
        try:
            self.gen(s[0], s[1], s[2], s[3], list(s[4]), bytearray(eval(s[5])), '', s[6])
        except TypeError:
            self.gen(s[0], s[1], s[2], s[3], list(s[4]), 'mining', '', s[6])
        self.update()
        return self

    def gen(self, author, froms, outs, outns, index, sign='signing', privkey='', t='now'):
        self.froms = froms  # input transactions
        self.outs = outs  # номера кошельков-адресатов
        self.outns = outns  # количество денег на каждый кошелек-адресат
        self.author = author  # тот, кто проводит транзакцию
        self.index = list(index)
        self.timestamp = time.time() if t == 'now' else t
        self.update()
        self.sign = sign_tnx(self, sign, privkey, t)
        self.hash = self.update()

    def is_valid(self, bch):
        """Returns validness of transaction.
        Checks:
        is sign valid
        are all money spent"""
        if self.index[1] == 0:
            is_first_tnx_valid(self, bch)
        elif self.author[0:4] == 'scaw':
            if not check_sc_award_tnx(bch, self.index, eval(self.author[4:])):
                return False
        elif not self.author[0:2] == 'sc':
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
        return cg.h(str(x))

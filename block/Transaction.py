import json
import cryptogr as cg
from itertools import chain
import time
from collections import Counter
#import net


def indexmany(a, k):
    return [i for i, e in enumerate(a) if e == k]


def rm_dubl_from_outs(outs, outns):
    newouts = []
    newoutns = []
    c = dict(Counter(outs))
    for o in c:
        if c[o] > 1:
            newouts.append(o)
            outn = 0
            for i in indexmany(outs, o):
                outn += outns[i]
            newoutns.append(outn)
        else:
            newouts.append(o)
            newoutns.append(outns[outs.index(o)])
    return newouts, newoutns


def is_first_tnx_valid(tnx, bch):
    if tnx.froms != [['nothing']] or tnx.author != 'mining' \
            or tnx.outs != bch[tnx.index[0]].creators or tnx.outns != mining.miningprice:
        return False
    else:
        return True


def is_tnx_money_valid(self, bch):
    inp = 0
    for o in self.outns:
        if round(o, 10) != o:
            return False
    for t in self.froms:  # how much money are available
        try:
            if not bch[int(t[0])].is_unfilled:
                tnx = bch[int(t[0])].txs[int(t[1])]
            else:
                if bch[int(t[0])].get_tnx(int(t[1])):
                    tnx = bch[int(t[0])].get_tnx(int(t[1]))
                else:
                    tnx = bch.get_block(int(t[0])).txs[int(t[1])]
            clean_outs = rm_dubl_from_outs([bch.pubkey_by_nick(out) for out in tnx.outs], tnx.outns)
            is_first = t[0] == 0 and t[1] == 0
            if not tnx.is_valid and not is_first:
                print(self.index, 'is not valid: from(', tnx.index, ') is not valid')
                return False
            if 'mining' in tnx.outs:
                return False
            if tnx.spent(bch, [self.index])[clean_outs[0].index(bch.pubkey_by_nick(self.author))]:
                print(self.index, 'is not valid: from(', tnx.index, ') is not valid as from')
                return False
            inp = inp + clean_outs[1][clean_outs[0].index(bch.pubkey_by_nick(self.author))]
        except Exception as e:
            print(self.index, 'is not valid: exception:', e)
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
        for i in range(len(self.outns)):
            self.outns[i] = round(self.outns[i], 10)
        self.update()
        return self

    def gen(self, author, froms, outs, outns, index, sign='signing', privkey='', t='now'):
        self.froms = froms  # transactions to get money from
        self.outs = outs  # destinations
        self.outns = outns  # values of money on each destination
        self.author = author
        self.index = list(index)
        self.timestamp = time.time() if t == 'now' else t
        for i in range(len(self.outns)):
            self.outns[i] = round(self.outns[i], 10)
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
            print("Log VSign: \n Index: {}. \nSign: {}. \nHash: {}. \nAuthor: {}. \n------------------------\n".format(
                str(self.index), self.sign, self.hash, self.author))
            print("Log TypeSign: \nSign: {}. \nHash: {}. \nAuthor: {}.".format(type(self.sign), type(self.hash),
                                                                               type(self.author)))
            sign_bytes = bytes(self.sign)
            if not cg.verify_sign(sign_bytes.decode(encoding="utf8", errors="ignore"), self.hash, self.author):
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
        outs, outns = rm_dubl_from_outs(self.outs, self.outns)
        spent = [False] * len(outs)
        for block in bch:  # перебираем все транзакции в каждом блоке
            for tnx in block.txs[1:]:
                if list(self.index) in list(tnx.froms) and 'mining' not in tnx.outs and tnx.index not in exc:
                    spent[outs.index(tnx.author)] = True
        return spent

    def update(self):
        x = ''.join(chain(str(self.author), str(self.index), [str(f) for f in self.froms],
                          [str(f) for f in self.outs], [str(f) for f in self.outns], str(self.timestamp)))
        self.hash = cg.h(str(x))
        return cg.h(str(x))

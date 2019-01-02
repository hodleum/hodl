import json
import logging as log
import time as t
from collections import Counter
from hodl import cryptogr as cg
from .constants import nick_av, nick_min, nick_max


def timestamp(ts):
    return t.time() if ts == 'now' else ts


def indexmany(a, k):
    return [i for i, e in enumerate(a) if e == k]


def rm_dubl_from_outs(outs, outns):
    """
    Remove dublicated addresses from tnx's outs

    :param outs: list, tnx.outs
    :param outns: list, tnx.outns
    :return: clean outs: list, clean outns: list
    """
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


def is_tnx_money_valid(self, bch):
    """
    Validate tnx

    :param self: Transaction
    :param bch: Blockchain
    :return: validness(bool)
    """
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
            if bch.pubkey_by_nick(self.author) not in [bch.pubkey_by_nick(o) for o in tnx.outs] \
                    or tnx.spent(bch, [self.index])[clean_outs[0].index(bch.pubkey_by_nick(self.author))]:
                log.warning(str(self.index) + ' is not valid: from(' + str(tnx.index) + ') is not valid as from')
                return False
            inp += clean_outs[1][clean_outs[0].index(bch.pubkey_by_nick(self.author))]
        except Exception as e:
            log.warning(str(self.index) + ' is not valid: exception: ' + str(e))
            return False
    o = 0
    for n in self.outns:  # all money must be spent
        if n < 0 or round(n, 9) != n:
            log.warning('{} is not valid because outn < 0 or n not rounded'.format(str(self.index)))
            return False
        o += n
    if round(o, 9) != round(inp, 9):
        log.warning(str(self.index) + ' is not valid: not all money')
        return False
    return True


def sign_tnx(self, sign, privkey, t):
    """
    Sign tnx with privkey or use existing sign

    :param self: tnx
    :param sign: existing sign or 'signing'
    :param privkey: private key or nothing
    :param t: existing timestamp if privkey is 'signing' or something else
    :return: sign (str)
    """
    if sign == 'signing':
        self.sign = cg.sign(self.hash, privkey)
    else:
        self.sign = sign
    return self.sign


class Transaction:
    """
    Class for transaction.
    To create new transaction, use:
    tnx=Transaction()
    tnx.gen(parameters)
    """

    def __init__(self):
        self.froms = None
        self.outs = None
        self.outns = None
        self.author = None
        self.index = None
        self.timestamp = None
        self.sign = None
        self.hash = None

    def __str__(self):
        """Encodes transaction to str using JSON"""
        return json.dumps((self.author, self.froms, self.outs, self.outns, self.index,
                           self.sign, self.timestamp))

    @classmethod
    def from_json(cls, s):
        """Decodes transacion from str using JSON"""
        s = json.loads(s)
        self = cls()
        try:
            self.gen(s[0], s[1], s[2], s[3], list(s[4]), s[5], '', s[6])
        except TypeError:
            self.gen(s[0], s[1], s[2], s[3], list(s[4]), 'mining', '', s[6])
        for i in range(len(self.outns)):
            self.outns[i] = round(self.outns[i], 10)
        self.update()
        return self

    def gen(self, author, froms, outs, outns, index, sign='signing', privkey='', ts='now', sc=tuple()):
        for i in range(len(outns)):
            outns[i] = round(outns[i], 9)
        self.froms = froms    # transactions to get money from
        self.outs = outs    # destinations
        self.outns = outns    # values of money on each destination
        self.author = author
        self.sc = list(sc)    # index of sc connected with transaction or [] if there is no
        self.index = list(index)
        self.timestamp = timestamp(ts)
        for i in range(len(self.outns)):
            self.outns[i] = round(self.outns[i], 10)
        self.update()
        self.sign = sign_tnx(self, sign, privkey, t)
        self.update()

    def is_valid(self, bch):
        """Returns validness of transaction.
        Checks:
        is sign valid
        are all money spent
        """
        # check outs and outns are not empty
        if (not (self.outs and self.outns)) and not self.sc:
            log.warning('{} is not valid: outs or outns are empty and there is no connected sc'.format(str(self.index)))
            return False
        # check validness of nick definition
        if self.author.count(';') == 2:
            if bch.pubkey_by_nick(self.author.split(';')[1], self.index)\
                    or not nick_min <= len(self.author.split(';')[1]) <= nick_max \
                    or set(list(self.author.split(';')[1])).issubset(nick_av):   # todo: control nick emission
                log.warning('{} is not valid: nick is wrong'.format(str(self.index)))
                return False
        elif self.author.count(';') == 3:
            if bch.pubkey_by_nick(self.author.split(';')[1], self.index) != self.author.split(';')[0]:
                # todo: control nick emission
                log.warning('{} is not valid: nick is wrong'.format(str(self.index)))
                return False
        # check sign
        try:
            if not cg.verify_sign(self.sign, self.hash, bch.pubkey_by_nick(self.author), bch):
                log.warning(str(self.index) + ' is not valid: sign is wrong')
                return False
        except Exception as e:
            log.warning(str(self.index) + ' is not valid: exception while checking sign: ' + str(e))
        # validate transaction money, for example froms and outs should be equal
        if not is_tnx_money_valid(self, bch):
            log.warning('{} is not valid: money calculated wrong'.format(str(self.index)))
            return False
        self.update()
        return True

    def __eq__(self, other):
        """Compare with other tnx"""
        return self.hash == other.hash

    def spent(self, bch, exc=tuple()):
        """
        Checks if money from transaction are spent

        :param bch: Blockchain
        :param exc: txs to exclude
        :return: Is transaction used by other transaction
        """
        outs, outns = rm_dubl_from_outs(self.outs, self.outns)
        outs = [bch.pubkey_by_nick(o) for o in outs]
        spent = [False] * len(outs)
        for block in bch:  # each tnx in each block
            for tnx in block.txs[1:]:
                if tuple(self.index) in [tuple(from_ind) for from_ind in tnx.froms] and tnx.index not in exc and \
                        bch.pubkey_by_nick(tnx.author) in outs:
                    spent[outs.index(bch.pubkey_by_nick(tnx.author))] = True
        return spent

    def update(self):
        """
        Update hash
        """
        x = json.dumps([self.author, self.froms, self.outs, self.outns, self.sc, self.timestamp])
        self.hash = cg.h(str(x))

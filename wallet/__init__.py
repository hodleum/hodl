# TODO: docstring
# TODO: move code from __init__.py


import json
import logging as log
import cryptogr as cg
import block
from block import mining

bch = block.Blockchain()
wallets = []


class NotEnoughMoney(Exception):
    pass


class Wallet:
    def __init__(self, keys=cg.gen_keys, filename="bch.db"):  # TODO: Value is not used; Type hints
        try:
            keys = keys()
        except TypeError:
            pass
        self.privkey, self.pubkey = keys

    def new_transaction(self, outs, outns, nick=''):  # TODO: Type hints
        """
        Performs tnx
        :param outs: wallets to send money to
        :param outns: amounts of money to send to outs
        :param nick: set nick
        :return tnx index
        :rtype: list
        """
        out = 0
        for i in range(len(outns)):
            outns[i] = round(outns[i], 10)
            out += outns[i]
        froms = []
        o = 0  # TODO: Len of variable name < 3
        for i in range(len(bch)):
            for tnx in bch[i].txs:
                if bch.pubkey_by_nick(self.pubkey) in [bch.pubkey_by_nick(out) for out in tnx.outs] and \
                        not tnx.spent(bch)[block.rm_dubl_from_outs(tnx.outs, tnx.outns)[0].index(
                            bch.pubkey_by_nick(self.pubkey))]:
                    clean_outs = block.rm_dubl_from_outs(
                        [bch.pubkey_by_nick(out) for out in tnx.outs],
                        tnx.outns)
                    o += clean_outs[1][clean_outs[0].index(bch.pubkey_by_nick(self.pubkey))]
                    froms.append(tnx.index)
                    if o >= out:
                        break
            if o >= out:
                break
        else:
            raise NotEnoughMoney('Needed: ' + str(out) + ', balance: ' + str(o))
        if o != out:
            outns.append(o - out)
            outs.append(self.pubkey)
        if not nick:
            author = self.pubkey
        else:
            author = self.pubkey + ';' + nick + ';'
        ind = bch.new_transaction(author, froms, outs, outns, privkey=self.privkey)
        log.info('wallet.new_transaction: outns: {}, len(outs): {}, index: {}'.format(str(outns), str(len(outs)),
                                                                                      str(ind)))
        return ind

    def new_sc(self, code, memsize=10000000, lang="js"):  # TODO: Type hints
        """
        Create smart contract
        :param code: SC's code
        :type code: str
        :param memsize: SC's memory size
        :type memsize: int
        :param lang: SC type
        :type lang: str
        """
        log.info('wallet.new_sc. Type: {}, memory size is {}'.format(lang, str(memsize)))
        sc_index = bch.new_sc(code, self.pubkey, self.privkey, memsize, lang)
        bch[sc_index[0]] = bch[sc_index[0]].update(bch)
        log.info('wallet.new_sc done: sc created')
        return sc_index

    def my_money(self):
        return bch.money(self.pubkey)

    @staticmethod
    def act():
        # TODO: docstring
        if bch[-1].is_full:
            bch.append(mining.mine(bch))

    def set_nick(self, nick):  # TODO: Type hints
        # TODO: docstring
        self.new_transaction([self.pubkey], [0], nick=nick)
        self.pubkey = nick

    def __str__(self):
        return json.dumps((self.privkey, self.pubkey))

    @classmethod
    def from_json(cls, st):
        return cls(json.loads(st))


def new_wallet(keys=cg.gen_keys, filename="bch.db"):  # TODO: Type hints
    # TODO: docstring
    w = Wallet(keys, filename)  # TODO: Len of variable name < 3
    wallets.append(w)
    return w


def sync_loop():
    pass   # todo: run sync

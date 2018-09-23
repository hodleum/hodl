import time
import json
import logging as log
import cryptogr as cg
import sync
import block
import mining

bch = block.Blockchain()
wallets = []


class NotEnoughMoney(Exception):
    pass


class Wallet:
    def __init__(self, keys=cg.gen_keys, filename="bch.db"):
        try:
            keys = keys()
        except TypeError:
            pass
        self.privkey, self.pubkey = keys

    def new_transaction(self, outs, outns, nick=''):
        """Performs tnx"""
        out = 0
        for i in range(len(outns)):
            outns[i] = round(outns[i], 10)
            out += outns[i]
        froms = []
        o = 0
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
        bch.new_transaction(author, froms, outs, outns, privkey=self.privkey)
        log.info('wallet.new_transaction: outns: {}, len(outs): {}, index: {}'.format(str(outns), str(len(outs)),
                                                                                      str(bch[-1].txs[-1].index)))

    def my_money(self):
        return bch.money(self.pubkey)

    @staticmethod
    def act():
        if bch[-1].is_full:
            bch.append(mining.mine(bch))

    def set_nick(self, nick):
        self.new_transaction([self.pubkey], [0], nick=nick)
        self.pubkey = nick

    def __str__(self):
        return json.dumps((self.privkey, self.pubkey))

    @classmethod
    def from_json(cls, st):
        return cls(json.loads(st))


def new_wallet(keys=cg.gen_keys, filename="bch.db"):
    w = Wallet(keys, filename)
    wallets.append(w)
    return w


def sync_loop():
    pass   # todo: run sync

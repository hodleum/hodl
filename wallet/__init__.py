import cryptogr as cg
from sync import loop
import block
import mining
import time
import json


bch = block.Blockchain()
wallets = []


class Wallet:
    def __init__(self, keys=cg.gen_keys):
        try:
            keys = keys()
        except:
            pass
        self.privkey, self.pubkey = keys

    def new_transaction(self, outs, outns):
        """Performs tnx"""
        out = 0
        for i in range(len(outns)):
            outns[i] = round(outns[i], 10)
            out += outns[i]
        if out > bch.money(self.pubkey):
            return False
        froms = []
        o = 0
        for i in range(len(bch)):
            for tnx in bch[i].txs:
                if self.pubkey in [bch.pubkey_by_nick(out) for out in tnx.outs] and 'mining' not in tnx.outs:
                    if not tnx.spent(bch)[block.rm_dubl_from_outs(tnx.outs, tnx.outns)[0].index(self.pubkey)]:
                        o += block.rm_dubl_from_outs([bch.pubkey_by_nick(out) for out in tnx.outs], tnx.outns)[1][block.rm_dubl_from_outs([bch.pubkey_by_nick(out) for out in tnx.outs], tnx.outns)[0].index(self.pubkey)]
                        froms.append(tnx.index)
                        if o >= out:
                            break
            if o >= out:
                break
        if o != out:
            outns.append(o - out)
            outs.append(self.pubkey)
        bch.new_transaction(self.pubkey, froms, outs, outns, privkey=self.privkey)

    def my_money(self):
        return bch.money(self.pubkey)

    def act(self):
        if bch[-1].is_full:
            bch.append(mining.mine(bch))

    def __str__(self):
        return json.dumps((self.privkey, self.pubkey))

    @classmethod
    def from_json(cls, st):
        return cls(json.loads(st))


def new_wallet():
    wallets.append(Wallet())


def sync_loop():
    loop([w.privkey, w.pubkey for w in wallets])

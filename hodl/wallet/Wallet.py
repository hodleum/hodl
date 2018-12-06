"""
HODL WALLET

Wallet is a high-level class for wallet

To create wallet:
    wallet = new_wallet()

Main methods:
    Wallet.new_transaction creates transaction
    Wallet.new_sc creates smart contracts
    Wallet.my_money returns balance of wallet
    Wallet.set_nick sets nick

TODO mining tools in wallet
TODO requests to smart contracts
"""
import json
import logging as log
import cryptogr as cg
import block
from block.Blockchain import Blockchain
from block.Transaction import rm_dubl_from_outs
from block import mining


bch = Blockchain()
wallets = []


class NotEnoughMoney(Exception):
    pass


class Wallet:
    def __init__(self, keys=None):
        if not keys:
            keys = cg.gen_keys()
        self.privkey, self.pubkey = keys

    def new_transaction(self, outs, outns, nick=''):
        """
        Performs tnx
        :param outs: wallets to send money to
        :type outs: list
        :param outns: amounts of money to send to outs
        :type outns: list
        :param nick: nick to set
        :type nick: str
        :return tnx index
        :rtype: list
        """
        out = 0
        for i in range(len(outns)):
            outns[i] = round(outns[i], 10)
            out += outns[i]
        froms = []
        o = 0
        for i in range(len(bch)):
            for tnx in bch[i].txs:
                if bch.pubkey_by_nick(self.pubkey) in [bch.pubkey_by_nick(out) for out in tnx.outs] and \
                        not tnx.spent(bch)[rm_dubl_from_outs(tnx.outs, tnx.outns)[0].index(
                            bch.pubkey_by_nick(self.pubkey))]:
                    clean_outs = rm_dubl_from_outs(
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

    def new_sc(self, code, memsize=10000000, lang="js"):
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
        log.info('wallet.new_sc done: sc created')
        return sc_index

    def my_money(self):
        return bch.money(self.pubkey)

    @staticmethod
    def act():
        """
        Appending blockchain with new blocks
        """
        if bch[-1].is_full:
            bch.append(mining.mine(bch))

    def set_nick(self, nick):
        """
        Set nick for wallet
        :param nick: nick to set
        :type nick: str
        """
        self.new_transaction([self.pubkey], [0], nick=nick)
        self.pubkey = nick

    def __str__(self):
        return json.dumps((self.privkey, self.pubkey))

    @classmethod
    def from_json(cls, st):
        return cls(json.loads(st))


def new_wallet(keys=None):
    """
    Create new wallet
    :param keys: keys of wallet
    :type keys: list
    :return: wallet
    :rtype Wallet
    """
    wallet = Wallet(keys)
    wallets.append(wallet)
    return wallet


def sync_loop():
    pass   # todo: run sync

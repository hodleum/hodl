import cryptogr as cg
from net import *


def listen_loop():
    """Listens, answers, listens, etc."""
    while True:
        new_listen_thread()

class Wallet:
    def __init__(self):
        self.privkey, self.pubkey = cg.gen_keys()

    def new_transaction(self, outs, outns):
        """Performs tnx"""
        out = 0
        for outn in outns:
            out += outn
        if out > bch.money(self.pubkey):
            return False
        froms = []
        # todo: write froms generation algorythm
        bch.new_transaction(self.pubkey, froms, outs, outns, privkey=self.privkey)

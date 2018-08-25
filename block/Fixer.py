import json
import mmh3
from block.constants import block_time, freeze
from mining.pool import Miners


class BlockFixer:
    """
    End of the block
    """
    def __init__(self, miners, tnxlen, sclen, tnx_last_h, sc_last_h):
        self.miners = miners
        self.tnxlen = tnxlen
        self.sclen = sclen
        self.tnx_last_h = tnx_last_h
        self.sc_last_h = sc_last_h
        self.update_hash()

    @classmethod
    def from_bch(cls, bch, miners, n):
        return cls(miners.by_time(bch[n].timestamp, bch[n].timestamp + block_time - freeze),
                   len(bch[n].txs), len(bch[n].contracts), bch[n].txs[-1].h, bch[n].contracts[-1].h)

    def __str__(self):
        return json.dumps([str(self.miners), self.tnxlen, self.sclen, self.tnx_last_h, self.sc_last_h])

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        s[0] = Miners.from_json(s[0])
        return cls(*s)

    def update_hash(self):
        self.h = mmh3.hash(str(self))

    def __hash__(self):
        return mmh3.hash(str(self))

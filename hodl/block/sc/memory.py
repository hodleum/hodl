import json
import net2
from block.constants import sc_base_mem, one_peer_max_mem


class SCMemoryError(Exception):
    pass


class SCMemory:
    """
    Decentralized memory for smart contract
    """
    def __init__(self, sc, size):
        self.scind = sc
        self.size = size
        self.peers = []
        self.accepts = []
        # [{miner1:[cg.h(mem, miner1),
        #   [acceptions or declinations for this user(a/d, sign, address)]]} for part in memory]

    def distribute_peers(self):
        """
        Distribute memory between miners
        :return:
        """
        self.peers.sort()
        l = len(self)
        m = len(self.peers)
        opm = ((one_peer_max_mem * m)//l)
        n = (l//one_peer_max_mem) + 1
        if self.size <= sc_base_mem:
            self.accepts = []
        else:
            self.accepts = [{p: ['', []] for p in self.peers[i*opm:(i+1)*opm]} for i in range(n)]

    def __len__(self):
        return self.length

    def __str__(self):
        """
        Save memory to str so it can be restored
        :return:
        """
        return json.dumps([self.scind, self.size, self.peers, self.accepts])

    @classmethod
    def from_json(cls, s):
        """
        Restore memory from str
        :param s: str
        :return: SCMemory
        """
        l = json.loads(s)
        self = cls(l[0], l[1])
        self.peers = l[5]
        self.accepts = l[6]
        return self

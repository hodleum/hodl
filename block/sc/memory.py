import json
import net
from block.constants import sc_base_mem, one_peer_max_mem
from vpy.fs import FS


class SCMemoryError(Exception):
    pass


class SCMemory(FS):
    """
    Decentralized memory for smart contract
    """
    def __init__(self, sc, size):
        super().__init__()
        self.scind = sc
        self.size = size
        self.local = ''
        self.localind = [0, 0]    # indices of data to store locally
        self.length = 0
        self.peers = []
        self.accepts = []
        # [{miner1:[cg.h(mem, miner1),
        #   [acceptions or declinations for this user(a/d, sign, address)]]} for part in memory]

    def __getitem__(self, item):
        if item.start < 0:
            item.start = len(self) - item.start
        if item.stop < 0:
            item.stop = len(self) - item.stop
        if self.size > sc_base_mem:
            if item.start > self.localind[0] and item.stop < self.localind[1]:
                # todo: make request using net
                return get_sc_memory(self.scind, item.start, item.stop)
        else:
            return self.local[item]

    def __setitem__(self, key, value):
        if type(key) == slice:
            if key.start >= self.localind[0] and key.stop - self.localind[0] <= sc_base_mem:
                self.local[key.start - self.localind[0]:key.stop - self.localind[0]] = value
            elif self.localind[1] > key.start >= self.localind[0]:
                if key.stop <= self.localind[1]:
                    self.local[key.start - self.localind[0]:key.stop - self.localind[0]] = value
                else:
                    self.local[key.start - self.localind[0]:self.localind[1]] = value
            elif key.start <= self.localind[0] and self.localind[1] >= key.stop >= self.localind[0]:
                self.local[0:key.stop - self.localind[0]] = value
        else:
            if self.localind[1] > key > self.localind[0]:
                self.local = list(self.local)
                self.local[key] = value
                self.local = ''.join(self.local)

    def add(self, other):
        if len(self) + len(other) > self.size:
            raise SCMemoryError
        if len(self) + len(other) < sc_base_mem:
            self.localind[1] = len(self) + len(other)
            self.local += other
        self.length = len(self) + len(other)

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
        return json.dumps([self.scind, self.size, self.local, self.localind, self.length, self.peers, self.accepts])

    @classmethod
    def from_json(cls, s):
        """
        Restore memory from str
        :param s: str
        :return: SCMemory
        """
        l = json.loads(s)
        self = cls(l[0], l[1])
        self.local = l[2]
        self.localind = l[3]
        self.length = l[4]
        self.peers = l[5]
        self.accepts = l[6]
        return self

    def __delitem__(self, key):
        # length -= number of deleted elements
        # if local indices are higher than length, fix them
        # changes to local
        pass    # todo

    def clear(self):
        self.length = 0
        self.local = ''
        self.localind = [0, 0]

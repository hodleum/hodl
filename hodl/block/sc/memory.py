from hodl.block.constants import sc_base_mem, one_peer_mem
import json
import logging as log


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
        """
        log.info(f'distributing peers for {self.scind}')
        self.peers.sort()
        mem_len = len(self)
        peers_len = len(self.peers)
        segment_num = mem_len // one_peer_mem
        if peers_len < segment_num:
            raise SCMemoryError(f'Not enough peers. Peers_len: {peers_len}, segment num: {segment_num}')
        peers_per_segment = peers_len // segment_num
        self.accepts = []
        for i in range(segment_num):
            self.accepts.append({p: {'hash': None, 'sign': None, 'accepts': {}}
                                 for p in self.peers[peers_per_segment*i: peers_per_segment*(i + 1)]})
        if peers_len >= segment_num * peers_per_segment:
            for i, peer in enumerate(self.peers[segment_num * peers_per_segment:]):
                self.accepts[i][peer] = {}
        log.info(f'Peers for {self.scind} distributed')

    def push_memory(self, address, sign, mem_hash):
        """
        Update hash for miner's memory part

        :param address: miner
        :type address: str
        :param sign: sign hash
        :type sign: str
        :param mem_hash: hash
        :type mem_hash: str
        """
        for i in range(len(self.accepts)):
            if address in self.accepts[i].keys():
                self.accepts[i][address]['hash'] = mem_hash
                self.accepts[i][address]['sign'] = sign
                self.accepts[i][address]['accepts'] = []
                log.info(f'memory pushed in {self.scind}')
                return

    def clear_accepts(self):
        """
        Delete all accepts with invalid sign (for example, previous hash was sign)
        """
        for i in range(len(self.accepts)):
            for address in self.accepts[i].keys():
                mem_hash = self.accepts[i][address]['hash']
                for accept in self.accepts[i][address]['accepts']:
                    pass   # todo: verify accept (sign)

    def __len__(self):
        """
        Length of the memory

        :return: lenght
        :rtype: int
        """
        return self.size

    def __str__(self):
        """
        Save memory to str so it can be restored

        :return: Memory string representation
        :rtype: str
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
        self.peers = l[2]
        self.accepts = l[3]
        return self

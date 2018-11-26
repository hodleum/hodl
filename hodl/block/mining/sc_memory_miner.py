"""
Proof-of-keeping local mining algorithms
"""
import block
import cryptogr as cg
import json
import sqlite3


# todo: PoW miner which wants to run task gets memory from PoK miner and pushes it after running task


class PoKMiner:
    """
    Proof-of-keeping miner class
    This miner finds smart contracts which need memory miners.
    It attends pool and when any change is available or there is time to check miners validity
    miner writes changes to local database or calculates hash to proof validity.
    """
    def __init__(self, addr):
        self.mining_scs = []
        self.addr = addr
        self.conn = sqlite3.connect('db/pok-' + cg.h(addr))
        self.c = self.conn.cursor()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS blocks
                     (blockind integer, scind integer, n integer, mem text)''')
        self.conn.commit()

    def calculate_hash(self, mem):
        h = cg.h(json.dumps((mem.local, self.addr)))
        return h

    def mine(self, scind, bch):
        sc = bch[scind[0]].contracts[scind[1]]
        ns = []
        for i, a in enumerate(sc.memory.accepts):
            if self.addr in a:
                ns.append(i)
        if not ns:
            return
        else:
            for n in ns:
                pass    # todo
        b = bch[scind[0]]
        b.contracts[scind[1]] = sc
        bch[scind[0]] = b

    def become_peer(self, bch, scind):
        bch[scind[0]].contracts[scind[1]].memory.peers.append(self.addr)
        self.mining_scs.append(scind)

    def mining(self, bch):
        while True:
            for sc in self.mining_scs:
                self.mine(sc, bch)

    def handle_get_request(self, request):
        """
        Handle get request
        :param request: request
        :type request: str
        :return: answer if needed
        :rtype: str
        """
        request = json.loads(request)
        answer = ''
        # todo: get memory
        return answer

    def handle_set_request(self, request):
        """
        Handle set request
        :param request: request
        :type request: str
        :return: ''
        :type: str
        """
        request = json.loads(request)
        # todo: check miner and sign
        # todo: set memory
        return ''

    def __str__(self):
        return json.dumps((self.addr, self.mining_scs))

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        self = cls(s[0])
        self.mining_scs = s[1]
        return self

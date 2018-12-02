"""
Proof-of-keeping local mining algorithms
"""
import block
import cryptogr as cg
import json
import sqlite3


class NotMiningError(Exception):
    pass


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
        self.conn.execute('''CREATE TABLE IF NOT EXISTS scs
                     (scind text, n integer, mem text)''')
        self.conn.commit()

    def calculate_hash(self, mem, addr=None):
        if not addr:
            addr = self.addr
        h = cg.h(json.dumps((mem.local, addr)))
        return h

    def mine(self, scind, bch):
        sc = bch[scind[0]].contracts[scind[1]]
        ns = []
        for i, part in enumerate(sc.memory.accepts):
            if self.addr in part.keys():
                ns.append(i)
        if not ns:
            raise NotMiningError()
        else:
            for n in ns:
                # if needed, calculate and push hash
                # prove other's hashes
                pass    # todo
        b = bch[scind[0]]
        b.contracts[scind[1]] = sc
        bch[scind[0]] = b

    def become_peer(self, bch, scind):
        b = bch[scind[0]]
        b.contracts[scind[1]].memory.peers.append(self.addr)
        bch[scind[0]] = b
        self.mining_scs.append(scind)

    def mining(self, bch):
        while True:
            for sc in self.mining_scs:
                self.mine(sc, bch)

    def handle_get_request(self, request):
        """
        Handle get request
        :param request: request (JSON)
        :type request: str
        :return: answer if needed
        :rtype: str
        """
        request = json.loads(request)
        return self[request['scind']]

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

    def __getitem__(self, item):
        """
        Get smart contract memory
        :param item: SC's index
        :type item: list
        :return: memory of this SC
        :rtype: str
        """
        self.c.execute("SELECT * FROM scs WHERE scind=?", (str([int(e) for e in item]),))
        return self.c.fetchone()[2]

    def __setitem__(self, key, value):
        """
        Set smart contract memory
        :param key: SC's index
        :type key: list
        :param value: memory
        :type value: str
        """
        self.c.execute("""UPDATE scs SET mem = ? WHERE scind = ?""", (str(value), str([int(e) for e in key])))
        self.conn.commit()

    def __str__(self):
        return json.dumps((self.addr, self.mining_scs))

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        self = cls(s[0])
        self.mining_scs = s[1]
        return self

"""
Proof-of-keeping local mining algorithms
"""
from hodl import block
from hodl import cryptogr as cg
import json
import sqlite3
import logging as log
from threading import Thread


class PoKNotMiningError(Exception):
    pass


class PoKMiner:
    """
    Proof-of-keeping miner class
    This miner finds smart contracts which need memory miners.
    It attends pool and when any change is available or there is time to check miners validity
    miner writes changes to local database or calculates hash to proof validity.
    """
    def __init__(self, addr, privkey):
        self.mining_scs = []
        self.addr = addr
        self.privkey = privkey
        self.conn = sqlite3.connect('hodl/db/pok-' + cg.h(addr))
        self.c = self.conn.cursor()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS scs
                     (scind text, n integer, mem text)''')
        self.conn.commit()
        log.info('PoKMiner object created')

    def calculate_hash(self, scind, addr=None):
        """
        Calculate hash of memory and address
        :param scind: index (list) of smart contract, which memory will be taken for hash calculation
        :type scind: list
        :param addr: address to hash with memory
        :type addr: str
        :return: hash
        :rtype: str
        """
        mem = self[scind]
        if not addr:
            addr = self.addr
        h = cg.h(json.dumps((mem, addr)))
        return h

    def mine(self, scind, bch):
        """
        Mine one smart contract: calculate and push hash for self, prove others' hashes
        :param scind: Index of smart contract to mine
        :type scind: list
        :param bch: Blockchain
        :type bch: block.Blockchain
        """
        sc = bch[scind[0]].contracts[scind[1]]
        part = None
        for i, part in enumerate(sc.memory.accepts):
            if self.addr in part.keys():
                part = i
        if part is None:
            raise PoKNotMiningError()
        else:
            # calculate and push hash
            mem_hash = self.calculate_hash(scind)
            sc.memory.push_memory(self.addr, cg.sign(mem_hash, self.privkey), mem_hash)
            # prove others' hashes
            for addr in sc.memory.accepts[part].keys():
                mem_hash = self.calculate_hash(scind, addr)
                if mem_hash == sc.memory.accepts[part][addr]['hash'] and cg.verify_sign(
                        sc.memory.accepts[part][addr]['sign'], sc.memory.accepts[part][addr]['hash'],
                                       addr, []):
                    sc.memory.accepts[part][addr]['accepts'].append([self.addr, cg.sign(
                        json.dumps(('v', mem_hash, self.addr)), self.privkey)])
                # todo: debug
        b = bch[scind[0]]
        b.contracts[scind[1]] = sc
        bch[scind[0]] = b

    def become_peer(self, bch, scind):
        """
        Become PoK peer for SC
        :param bch: blockchain
        :type bch: Blockchain
        :param scind: index of SC to mine
        :type scind: list
        """
        b = bch[scind[0]]
        b.contracts[scind[1]].memory.peers.append(self.addr)
        bch[scind[0]] = b
        self.mining_scs.append(scind)

    def mining_thread(self, bch):
        """
        Start mining loop in thread
        :param bch: blockchain
        :type bch: Blockchain
        """
        def mining():
            log.info('PoK mining thread started')
            while True:
                for sc in self.mining_scs:
                    self.mine(sc, bch)
        Thread(target=mining, name="PoK").start()

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
        """
        Create this object's string representation
        """
        return json.dumps((self.addr, self.privkey, self.mining_scs))

    @classmethod
    def from_json(cls, s):
        """
        Restore PoKMiner object from its representation
        :param s: PoKMiner object's representation (str(pokminer_object))
        :type s: str
        """
        s = json.loads(s)
        self = cls(s[0], s[1])
        self.mining_scs = s[2]
        return self

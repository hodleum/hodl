"""
Proof-of-keeping local mining algorithms
"""
from hodl import block
from hodl import cryptogr as cg
import json
import sqlite3
import logging as log
from multiprocessing import Process


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
        """
        Init

        :param addr: address of miner
        :type addr: str
        :param privkey: miner's private key
        :type privkey: str
        """
        self.mining_scs = []
        self.addr = addr
        self.privkey = privkey
        self.conn = sqlite3.connect('db/pok-' + cg.h(addr), check_same_thread=False)
        self.c = self.conn.cursor()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS scs
                     (scind text, mem text)''')
        self.conn.commit()
        log.info('PoKMiner object created')

    def become_peer(self, bch, scind):
        """
        Become PoK peer for SC

        :param bch: blockchain
        :type bch: Blockchain
        :param scind: index of SC to mine
        :type scind: list
        """
        if scind in self.mining_scs:
            return
        # todo: do nothing if this SC doesn't needs PoK miners or if no space left
        b = bch[scind[0]]
        b.contracts[scind[1]].memory.peers.append(self.addr)
        bch[scind[0]] = b
        self.mining_scs.append(scind)
        self.add_sc(scind)
        log.info(f'became peer of SC {scind}')

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
        log.debug(f'calculating hash for SC {scind}')
        mem = self[scind]
        if not addr:
            addr = self.addr
        h = cg.h(json.dumps((mem, addr)))
        log.debug('hash calculated')
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
            raise PoKNotMiningError(f'No part in {scind}')
        log.info(f'part is not none in {scind}')
        # calculate and push hash
        mem_hash = self.calculate_hash(scind)
        sc.memory.push_memory(self.addr, cg.sign(mem_hash, self.privkey), mem_hash)
        log.debug('memory pushed')
        # prove others' hashes
        miners = sc.memory.accepts[part].keys()
        for addr in miners:
            log.debug(f'proving PoK miner {addr} in SC {scind}')
            mem_hash = self.calculate_hash(scind, addr)
            if mem_hash == sc.memory.accepts[part][addr]['hash'] and cg.verify_sign(
                    sc.memory.accepts[part][addr]['sign'], sc.memory.accepts[part][addr]['hash'], addr, []):
                sc.memory.accepts[part][addr]['accepts'].append([self.addr, cg.sign(
                    json.dumps(('v', mem_hash, self.addr)), self.privkey)])
        log.debug('all miners proved')
        b = bch[scind[0]]
        b.contracts[scind[1]] = sc
        bch[scind[0]] = b
        log.info(f'mining sc {scind} done')

    def main_process(self, bch):
        """
        Start mining loop in another process

        :param bch: blockchain
        :type bch: Blockchain
        """
        def mining():
            log.info('PoK mining thread started')
            while True:
                for sc in self.mining_scs:
                    try:
                        self.mine(sc, bch)
                    except PoKNotMiningError:
                        pass

        def become_peer_loop():
            while True:
                for i in range(len(bch)):
                    for j in range(len(bch[i].contracts)):
                        self.become_peer(bch, [i, j])
        Process(target=mining, name="PoK mining").start()
        Process(target=become_peer_loop, name="PoK discovering").start()

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
        res = self.c.fetchone()[1]
        return res

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

    def add_sc(self, key):
        """
        Add new SC to mine in local DB

        :param key: SC's index
        :type key: list
        """
        log.debug(f'adding SC {key} to db')
        self.c.execute("INSERT INTO scs VALUES (?, ?)", (str([int(e) for e in key]), ''))
        self.conn.commit()

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

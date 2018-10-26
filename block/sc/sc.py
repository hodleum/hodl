import json
import time
import logging as log
import cryptogr as cg
from block.sc.memory import SCMemory
from block.sc.executors.js.jstask import js
from block.sc.executors.js.jstools import CTX
from block.constants import sc_base_code_size, sc_memprice, sc_code_price, sc_price, sc_base_mem


# todo: remove tasks from smart contracts, create pool of calculating tasks with difficulty mark
# todo: smart contract's signs


def check_sc_award_tnx(bch, tnxind, sc):
    pass


class SmartContract:
    """
    Class for smart contracts (SC)
    SC.code stores smart contract's code.
    It can be splitted in many files.
    SC has messages and tasks.
    Messages are signed function calls.
    Tasks are task for computing.
    Memory is splitted into parts, which are stored with copies. (distribution is stored in SC.memory_distribution)
    Miner who wants to store data writes his public key to SC.mempeers.
    Miner who wants to calculate writes his public key to SC.calculators.
    After creating new block all miners become money.
    Storage miners calculate hash of data with their public keys and with other miners' public keys. Then they compare
    their answers.
    Calculating miners also compare their answers.
    """
    def __init__(self, code, author, index, memsize=sc_base_mem, langr="js"):
        log.info('new sc')
        self.code = code
        self.author = author
        self.index = index
        self.memory = SCMemory(self.index, memsize)
        self.msgs = []  # [[author, sign, msg:str, ans=None]]
        self.timestamp = time.time()
        self.calculators = []
        self.signs = []
        self.membs = []
        if langr == 'js':
            log.info('js task splitting')
            self.tasks = js[1](code)
            log.info('js task splitting done')
        self.awards = {}
        self.sign = ''
        self.memory_distribution = []   # [[Miners for part1]]
        self.signs = []
        self.h = self.sign_str()
        self.langr = langr
        log.info('new sc created')

    def sign_sc(self, privkey):
        self.sign = cg.sign(self.h, privkey)

    def execute_task(self):
        if not self.tasks:
            return
        if not self.tasks[0].done:
            self.tasks[0].run(str(CTX()))
            return
        for i, task in enumerate(self.tasks):
            if not task.done:
                task.run(self.tasks[i-1].context)
                return

    def __str__(self):
        """
        Encode contract to str
        :return: str
        """
        return json.dumps((self.code, self.author, self.index, self.msgs, self.timestamp, self.sign, str(self.memory)))

    @classmethod
    def from_json(cls, s):
        """
        Decode contract from str
        :param s: SC encoded to string
        :return: SC
        """
        self = cls(*json.loads(s)[0:3])
        self.msgs, self.timestamp, self.sign = json.loads(s)[3:6]
        self.memory = SCMemory.from_json(json.loads(s)[6])
        return self

    def __eq__(self, other):
        """
        Compare SCs
        :param other: SC
        :return: is equal
        """
        return self.__dict__ == other.__dict__

    def is_valid(self, bch):
        """
        Validate SC
        :param bch: Blockchain
        :return: validness(bool)
        """
        # todo: sign check
        pr = sc_price
        if self.memory.size > sc_base_mem:
            mp = ((self.memory.size - sc_base_mem) * sc_memprice)
            if mp < 0:
                mp = 0
            pr += mp
        pr = round(pr, 10)
        payed = bch.money('sc' + str(list(self.index)))
        if payed < pr:
            log.debug('sc not payed. payed: ' + str(payed) + ', needed: ' + str(pr))
            return False
        if not cg.verify_sign(self.sign, self.sign_str(), bch.pubkey_by_nick(self.author), bch):
            log.debug('not valid sign in sc')
            return False
        return True

    def validate_sign(self, o_sign):
        """
        Validate transaction made by smart contract
        :param o_sign: sign to verify
        :return: validness: bool
        """
        for sign in self.signs:
            if sign == o_sign:
                return True
        return False

    def calc_awards(self, bch):
        """
        Calculates how much to pay to miners.
        :param bch:Blockchain
        """
        self.awards = {}
        # Memory miners
        for p in self.memory.accepts:
            for m in p:
                acceptions = 0
                for w in p[m][1]:
                    for a in w:
                        if a[0] == 'a':
                            acceptions += 1
                if acceptions >= len(p[m][1]) * 0.7:
                    self.awards[m] = sc_memprice / (len(self.memory.accepts)*len(p))

        # Calculators
        # todo: calculators awards

    def distribute_tasks(self):
        """
        Distribute tasks between miners
        :return:
        """
        self.calculators.sort()
        for i in range(len(self.tasks)):
            for j in range(self.tasks[i][2]):
                try:
                    self.tasks[i][1][self.calculators[j]] = []
                    self.calculators.remove(self.calculators[j])
                except:
                    break

    def sign_str(self):
        return json.dumps((self.code, str(self.author), self.index, self.memory.size, self.timestamp))

    def verify_sign(self, sign):
        return sign in self.signs

    def update(self, bch):
        # todo: delete not valid tasks
        # todo: distribute miners if needed
        self.memory.distribute_peers()
        self.distribute_tasks()

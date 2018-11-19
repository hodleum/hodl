import json
import time
import logging as log
import cryptogr as cg
from block.sc.memory import SCMemory
from block.sc.executors.js.jstask import js
from block.sc.task import Task
from block.sc.executors.js.jstools import CTX
from block.constants import sc_base_code_size, sc_memprice, sc_code_price, sc_price, sc_base_mem


# todo: remove tasks from smart contracts, create pool of calculating tasks with difficulty mark
# todo: smart contract's signs


def check_sc_award_tnx(bch, tnxind, sc):
    pass


def jstask_to_task(scind, n, task):
    return Task(scind, n, 'js', task_data=str(task))


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
        self.code = code
        self.author = author
        self.index = index
        self.memory = SCMemory(self.index, memsize)
        self.timestamp = time.time()
        self.calculators = []
        self.signs = []
        self.membs = []
        self.n = 0
        self.tasks = None
        if langr == 'js':
            # todo: do not split code to tasks every time
            self.tasks = list(map(lambda task: jstask_to_task(self.index, self.n, task), js[1](code)))
            for i in range(len(self.tasks)):
                self.tasks[i].n = i
            self.n = len(self.tasks)
        self.awards = {}
        self.msg_tasks = []
        self.sign = ''
        self.memory_distribution = []   # [[Miners for part1]]
        self.signs = []
        self.h = self.sign_str()
        self.langr = langr

    def sign_sc(self, privkey):
        self.sign = cg.sign(self.h, privkey)

    def __str__(self):
        """
        Encode contract to str
        :return: str
        """
        return json.dumps((self.code, self.author, self.index, self.msg_tasks,
                           self.timestamp, self.sign, str(self.memory), [str(task) for task in self.tasks],
                           self.n))

    @classmethod
    def from_json(cls, s):
        """
        Decode contract from str
        :param s: SC encoded to string
        :return: SC
        """
        s = json.loads(s)
        self = cls(*s[0:3])
        self.msg_tasks, self.timestamp, self.sign = s[3:6]
        self.memory = SCMemory.from_json(s[6])
        self.tasks = [Task.from_json(task) for task in s[7]]
        self.n = s[8]
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

    def net_request(self, request_sender, request, bch):
        if self.langr == 'js':
            task = js[3](request_sender, request)
        else:
            return
        self.msg_tasks.append(task)
        b = bch[-1]
        b.sc_tasks.append(task)
        bch[-1] = b

    def msg_request(self, sender, msg, bch):
        if self.langr == 'js':
            task = js[2](sender, msg)
        else:
            return
        self.msg_tasks.append(task)
        b = bch[-1]
        b.sc_tasks.append(task)
        bch[-1] = b

    def update(self, bch):
        log.info(f'SC.update, len(self.tasks) is {len(self.tasks)}')
        # todo: process self.msg_tasks
        if len(self.tasks) != 0:
            try:
                index = [hash(task) for task in bch[-1].sc_tasks].index(hash(self.tasks[0]))
                if bch[-1].sc_tasks[index].done:   # todo: search in previous block too
                    if self.tasks[0].task_class == 'js':
                        self.tasks[1].task = str(self.tasks[0].task)
                    self.tasks.pop(0)
                log.info(f"SC.update:adding task with n={self.tasks[1].n} to last block (block number {len(bch) - 1}), "
                         f"len(bch[-1].sc_tasks) is {len(bch[-1].sc_tasks)}")
            except ValueError:
                log.info(f"SC.update:adding this sc's first task to last block. len(bch[-1].sc_tasks) "
                         f"is {len(bch[-1].sc_tasks)}")
            b = bch[-1]
            b.sc_tasks.append(self.tasks[0])
            bch[-1] = b
            log.info(f'SC.update:task added to block. len(bch[-1].sc_tasks) is {len(bch[-1].sc_tasks)}, '
                     f'len(b.sc_tasks) is {len(b.sc_tasks)}')
        # todo: delete not valid tasks
        # todo: memory

import json
import time
import os
import logging as log
import vpy
import cryptogr as cg
from block.sc.memory import SCMemory
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
    def __init__(self, code, author, index, computing=False, calc_repeats=3,
                 memsize=sc_base_mem, codesize=sc_base_code_size):
        self.code = code
        self.author = author
        self.index = index
        self.memory = SCMemory(self.index, memsize)
        self.msgs = []  # [[message func, message args(the first is message's sender), str(list(sender's sign)), is executed]]
        self.timestamp = time.time()
        self.calculators = []
        self.computing = computing
        self.codesize = codesize
        self.signs = []
        self.membs = []
        self.calc_repeats = calc_repeats
        self.awards = {}
        self.sign = ''
        self.memory_distribution = []   # [[Miners for part1]]
        self.signs = []
        self.h = self.sign_str()

    def sign_sc(self, privkey):
        self.sign = cg.sign(self.h, privkey)

    def execute(self, func='', args=tuple(), is_task=False):
        """
        Execute SC's code.
        SC can modify its memory, read blockchain, provide txs
        :param func: function to execute(if executing msg or task)
        :param args: func's args
        :param is_task: if executing task, no timeout needed
        """
        # todo: run with vpy
        file = open('tmp/__init__.py', 'w')
        file.close()
        file = open('sc_main.py', 'w')
        if func == '':
            file.writelines(['from tmp import sc\n', 'import json\n'])
        else:
            file.writelines(['from tmp import sc\n', 'import json\n',
                             "args = {}\n".format(args), 'sc.{}(*args)\n'.format(func)])
        file.close()
        file = open('tmp/sc.py', 'w')
        file.writelines(['ind = ' + str(self.index) + '\n'] + self.code)
        file.close()
        file = open('tmp/sc.mem', 'w')
        file.writelines(str(self.memory))
        file.close()
        file = open('tmp/sc.msgs', 'w')
        file.writelines([str(mem) for mem in list(self.msgs)])
        file.close()
        file = open('tmp/sc.tasks', 'w')
        file.writelines([json.dumps(task) for task in list(self.tasks)])
        file.close()
        file = open('tmp/sc.ind', 'w')
        file.writelines([json.dumps(self.index)])
        file.close()
        open('tmp/sc.txs', 'w').close()
        mount_str = ''
        mount_temp = ' -v "$(pwd)"/{}:/home/hodl/{}:ro'
        l = os.listdir()
        l.remove('tmp')
        if not is_task:
            timeout = '--stop-timeout 1'
        else:
            timeout = ''
        for f in l:
            mount_str += mount_temp.format(f, f)
        run_str = 'docker run {} -v "$(pwd)/tmp":/home/hodl/tmp{} hodl-container python3 ' \
                  '/home/hodl/sc_main.py'.format(mount_str, timeout)
        os.system(run_str)   # todo: replace with docker lib
        file = open('tmp/sc.mem', 'r')
        self.memory = SCMemory.from_json(file.readline())
        file.close()
        file = open('tmp/sc.signs', 'r')
        self.signs.append(json.loads(file.read()))
        file.close()

    def __str__(self):
        """
        Encode contract to str
        :return: str
        """
        return json.dumps((self.code, self.author, self.index, self.computing, self.calc_repeats, self.msgs,
                           self.codesize, self.timestamp, self.sign, str(self.memory)))

    @classmethod
    def from_json(cls, s):
        """
        Decode contract from str
        :param s: SC encoded to string
        :return: SC
        """
        self = cls(*json.loads(s)[0:4])
        self.msgs, self.codesize, self.timestamp, self.sign = json.loads(s)[5:9]
        self.memory = SCMemory.from_json(json.loads(s)[9])
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
        pr = sc_price
        if self.memory.size > sc_base_mem or self.codesize > sc_base_code_size:
            mp = ((self.memory.size - sc_base_mem) * sc_memprice)
            if mp < 0:
                mp = 0
            cp = ((self.codesize - sc_base_code_size) * sc_code_price)
            if cp < 0:
                cp = 0
            pr += mp + cp
        pr = round(pr, 10)
        payed = bch.money('sc' + str(list(self.index)))
        if payed < pr:
            log.debug('sc not payed. payed: ' + str(payed) + ', needed: ' + str(pr))
            return False
        if not cg.verify_sign(self.sign, self.sign_str(), bch.pubkey_by_nick(self.author)):
            log.debug('not valid sign in sc')
            return False
        return True

    def validate_tnx(self, tnx, bch):
        """
        Validate transaction made by smart contract
        :param tnx: Transaction
        :param bch: Blockchain
        :return: validness: bool
        """
        for tnx in self.txs:
            if self.index == tnx.index:
                break
        else:
            return False
        return True

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

    def handle_messages(self):
        """
        Handle all messages(commands) sent to SC
        :return:
        """
        for i in range(len(self.msgs)):
            if not self.msgs[i][-1]:
                if cg.verify_sign(self.msgs[i][2], json.dumps([self.msgs[i][0], self.msgs[i][1]]),
                                  self.msgs[i][1][0]):
                    self.execute(self.msgs[i][0], self.msgs[i][1])
                    self.msgs[i][-1] = True

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
        return json.dumps((self.code, str(self.author), self.index,
                           self.computing, self.calc_repeats, self.memory.size, self.codesize, self.timestamp))

    def verify_sign(self, sign):
        return sign in self.signs

    def update(self, bch):
        # todo: delete not valid tasks

        # todo: distribute miners if needed
        self.memory.distribute_peers()
        self.distribute_tasks()

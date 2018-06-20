import json
import time
import cryptogr as cg
import os


sc_base_mem = 10000000
sc_base_code_size = 5000000
sc_memprice = 0.001
sc_max_code_size = 1000000000
sc_code_price = 10**(-6)
sc_price = 0.01
one_peer_max_mem = 4000000
sc_award_from = 1
sc_award_to = 5


class SCMemoryError(Exception):
    pass


def check_sc_award_tnx(bch, tnxind, sc):
    pass


class Smart_contract:
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
    def __init__(self, code, author, index, computing=False, tasks=[], calc_repeats=3,
                 memsize=sc_base_mem, codesize=sc_base_code_size):
        self.code = code
        self.author = author
        self.index = index
        self.memory = SCMemory(self.index, memsize)
        self.msgs = []  # [[message func, message args(the first is message's sender), str(list(sender's sign)), is executed]]
        self.timestamp = time.time()
        self.calculators = []
        self.computing = computing
        self.tasks = tasks  # [[command, {miner:[cg.h(str(ans)+miner), time when cg.h added, ans(appended after)]]},
        # repeats, award, author, len(bch) when publishing, tnx for awards's index, solved]]
        self.codesize = codesize
        self.txs = []
        self.membs = []
        self.calc_repeats = calc_repeats
        self.awards = {}
        self.sign = ''
        self.memory_distribution = []   # [[Miners for part1]]

    def sign_sc(self, privkey):
        self.sign = cg.sign(json.dumps((self.code, str(self.author), self.index, self.computing, self.calc_repeats, self.memory.size,
                           self.codesize, self.timestamp)), privkey)

    def execute(self, func='', args=[], is_task=False):
        """
        Execute SC's code.
        SC can modify its memory, read blockchain, provide txs
        :param func: function to execute(if executing msg or task)
        :param args: func's args
        :param is_task: if executing task, no timeout needed
        """
        # todo: allow SC to confirm its memory, not to calculate it every time
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
        file = open('tmp/sc.tasks', 'r')
        self.tasks = [json.loads(task) for task in file.readlines()]
        file.close()
        file = open('tmp/sc.txs', 'r')
        self.txs.append([Transaction.from_json(tnxstr) for tnxstr in file.readlines()])
        file.close()

        # todo: sc tnx

    def __str__(self):
        """
        Encode contract to str
        :return: str
        """
        return json.dumps((self.code, self.author, self.index, self.computing, self.tasks, self.calc_repeats, self.msgs,
                           self.codesize, self.timestamp, self.sign, str(self.memory)))

    @classmethod
    def from_json(cls, s):
        """
        Decode contract from str
        :param s: SC encoded to string
        :return: SC
        """
        self = cls(*json.loads(s)[0:5])
        self.msgs, self.codesize, self.timestamp, self.sign = json.loads(s)[6:10]
        self.memory = SCMemory.from_json(json.loads(s)[10])
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
        if self.codesize > sc_max_code_size:
            print('too much code in sc')
            return False
        pr = sc_price
        if self.memory.size > sc_base_mem or self.codesize > sc_base_code_size:
            mp = ((self.memory.size - sc_base_mem) * sc_memprice)
            if mp < 0:
                mp = 0
            cp = ((self.codesize - sc_base_code_size) * sc_code_price)
            if cp < 0:
                cp = 0
            pr += mp + cp
        payed = 0
        for b in bch:
            for tnx in b.txs:
                if tnx.author == self.author and 'sc' + str(self.index) + 'payment' in tnx.outs:
                    payed += tnx.outns[tnx.outs.index('sc' + str(self.index) + 'payment')]
        if not payed >= pr:
            print('sc not payed. payed:', payed, 'needed:', pr)
            return False
        if not cg.verify_sign(self.sign, json.dumps((self.code, str(self.author), self.index, self.computing, self.calc_repeats, self.memory.size,
                           self.codesize, self.timestamp)), self.author):
            print('not valid sign in sc')
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
        for i, task in enumerate(self.tasks):
            if not task[-1]:
                for m in task[1]:
                    a = 0
                    last_time = 0
                    for m in task[1]:
                        if len(task[1][m]) > 1:
                            a += 0
                            last_time = max((task[1][m][1], last_time))
                    if a / len(task[1]) > 0.8 and last_time - time.time() > 600:
                        ans = [task[1][m][2] for m in task[1]]
                        c = [ans.count(an) for an in ans]
                        right_ans = ans[c.index(max(c))]
                        for m in task[1]:
                            if task[1][m][2] == right_ans:
                                if sc_award_to > task[3] > sc_award_from:
                                    self.awards[m] = task[3] / len(task[1])
                                elif task[3] > sc_award_to:
                                    self.awards[m] = sc_award_to / len(task[1])
                task[-1] = True

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

    def update(self, bch):
        # delete not valid tasks

        # distribute miners if needed
        self.memory.distribute_peers()
        self.distribute_tasks()


class SCMemory:
    def __init__(self, sc, size):
        self.scind = sc
        self.size = size
        self.local = ''
        self.localind = [0, 0]
        self.length = 0
        self.peers = []
        self.accepts = []   # [{miner1:[cg.h(mem, miner1), [acceptions or declinations for this user(a/d, sign, address)]]} for part in memory]

    def __getitem__(self, item):
        if item.start < 0:
            item.start = len(self) - item.start
        if item.stop < 0:
            item.stop = len(self) - item.stop
        if self.size > sc_base_mem:
            if item.start > self.localind[0] and item.stop < self.localind[1]:
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

    def __add__(self, other):
        if len(self) + len(other) > self.size:
            raise SCMemoryError
        if len(self) + len(other) < sc_base_mem:
            self.localind[1] = len(self) + len(other)
            self.local += other
        self.length = len(self) + len(other)
        return self

    def distribute_peers(self):
        """
        Distribute memory between miners
        :return:
        """
        self.peers.sort()
        l = len(self)
        m = len(self.peers)
        opm = ((one_peer_max_mem * m)//(l))
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

    def clear(self):
        self.length = 0
        self.local = ''
        self.localind = [0, 0]

import json
import time
import cryptogr as cg
import os
import net


sc_base_mem = 10000000
sc_base_code_size = 5000000
sc_memprice = 10**(1/10)
sc_max_code_size = 1000000000
sc_code_price = 10**(1/6)
sc_price = 0.01
one_peer_max_mem = 40000000


class Smart_contract:
    def __init__(self, code, author, index, computing=False, tasks=[], mem_copies=3, calc_repeats=3,
                 memsize=sc_base_mem, codesize=sc_base_code_size):
        self.code = code
        self.author = author
        self.index = index
        self.memory = []
        self.msgs = []  # [[message func, message args(the first is message's sender), str(list(sender's sign)), is executed]]
        self.timestamp = time.time()
        self.computing = computing
        self.tasks = tasks  # [[command, {miner:[[acceptions or declinations(a/d, sign, address)], time solved]},
        # repeats, award, done]]
        self.mempeers = []
        self.memsize = memsize
        self.codesize = codesize
        self.txs = []
        self.membs = []
        self.mem_copies = mem_copies
        self.calc_repeats = calc_repeats
        self.awards = {}
        self.sign = ''
        self.memory_distribution = []   # [[Miners for part1]]

    def sign_sc(self, privkey):
        self.sign = cg.sign(json.dumps((self.code, str(self.author), self.index, self.computing, self.tasks,
                           self.mem_copies, self.calc_repeats, self.msgs, self.mempeers, self.memsize,
                           self.codesize, self.timestamp)), privkey)

    def execute(self, func='', args=[]):
        """smart contract's execution"""
        file = open('tmp/__init__.py', 'w')
        file.close()
        file = open('sc_main.py', 'w')
        if func == '':
            file.writelines(['from tmp import sc\n'])
        else:
            file.writelines(['from tmp import sc\n', 'import json\n',
                             "args = {}\n".format(args), 'sc.{}(*args)\n'.format(func)])
        file.close()
        file = open('tmp/sc.py', 'w')
        file.writelines(['ind = ' + str(self.index) + '\n'] + self.code)
        file.close()
        file = open('tmp/sc.mem', 'w')
        file.writelines(json.dumps(self.memory))
        file.close()
        file = open('tmp/sc.msgs', 'w')
        file.writelines([str(mem) for mem in list(self.msgs)])
        file.close()
        file = open('tmp/sc.tasks', 'w')
        file.writelines([json.dumps(task) for task in list(self.tasks)])
        file.close()
        open('tmp/sc.txs', 'w').close()
        os.system('docker run -v "$(pwd)":/home/hodl -v "$(pwd)/bch.db":/home/hodl/bch.db:ro -v "$(pwd)/tmp":/home/hodl/tmp hodl-container python3 /home/hodl/sc_main.py')
        file = open('tmp/sc.mem', 'r')
        self.memory = json.loads(file.readline())
        file.close()
        file = open('tmp/sc.tasks', 'r')
        self.tasks = [json.loads(task) for task in file.readlines()]
        file.close()
        file = open('tmp/sc.txs', 'r')
        self.txs.append([Transaction.from_json(tnxstr) for tnxstr in file.readlines()])
        file.close()

        # todo: sc tnx

    def __str__(self):
        """Encodes contract to str"""
        return json.dumps((self.code, self.author, self.index, self.computing, self.tasks,
                           self.mem_copies, self.calc_repeats, self.msgs, self.mempeers, self.memsize,
                           self.codesize, self.timestamp, str(list(self.sign))))

    @classmethod
    def from_json(cls, s):
        """Decodes contract from str"""
        self = cls(*json.loads(s)[0:7])
        self.msgs, self.membs, self.memsize, self.codesize, self.timestamp, self.sign = json.loads(s)[7:]
        self.sign = bytes(eval(self.sign))
        return self

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def is_valid(self, bch):
        if self.codesize > sc_max_code_size:
            return False
        pr = sc_price
        if self.memsize > sc_base_mem or self.codesize > sc_base_code_size:
            pr += ((self.memsize - sc_base_mem) * sc_memprice) + ((self.codesize - sc_base_code_size) * sc_code_price)
        payed = 0
        for b in bch:
            for tnx in b.txs:
                if tnx.author == self.author and str(self.index) + 'payment' in tnx.outs:
                    payed += tnx.outns[tnx.outs.index(str(self.index) + 'payment')]
        if not payed >= pr:
            return False
        if not cg.verify_sign(self.sign, json.dumps((self.code, str(self.author), self.index, self.computing, self.tasks,
                           self.mem_copies, self.calc_repeats, self.msgs, self.mempeers, self.memsize,
                           self.codesize, self.timestamp)), self.author):
            return False
        return True

    def calc_awards(self):
        self.awards = {}
        for task in self.tasks:
            for w in task[1].keys():
                accepts = 0
                for a in task[1][w][0]:
                    if a[0] == 'a':
                        accepts += 1
                if accepts < (0.7 * task[2]):
                    if w in self.awards.keys():
                        self.awards[w].append([task[3], task[1][w][1]])
                    else:
                        self.awards[w] = [task[3]]

    def handle_messages(self):
        for i in range(len(self.msgs)):
            if not self.msgs[i][-1]:
                if cg.verify_sign(bytes(eval(self.msgs[i][2])), json.dumps([self.msgs[i][0], self.msgs[i][1]]),
                                  self.msgs[i][1][0]):
                    self.execute(self.msgs[i][0], self.msgs[i][1])
                    self.msgs[i][-1] = True

    def __eq__(self, other):
        v = True
        if self.__dict__.keys() != other.__dict__.keys():
            print('sc.__eq__ keys not equal', self.__dict__.keys(), other.__dict__.keys())
            v = False
        for k in self.__dict__.keys():
            if self.__dict__[k] != other.__dict__[k]:
                print(k, self.__dict__[k], other.__dict__[k])
        return str(self) == str(other)

    def distribute_peers(self):
        self.mempeers.sort()
        l = len(self.memory)
        m = len(self.mempeers)
        n = ((one_peer_max_mem * m)//l)+1
        if self.memsize <= sc_base_mem:
            self.memory_distribution = 'all'
        else:
            self.memory_distribution = [[self.mempeers[i*n:(i+1)*n]] for i in range(l//n)]

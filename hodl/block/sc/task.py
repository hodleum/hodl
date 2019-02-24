import json
from collections import Counter
from hodl.block.sc.executors.js.jstask import js
from hodl.block.constants import MAXMINERS
import mmh3


class TaskMiner:
    def __init__(self, address='', difficulty=None, result_hash=None):
        """
        Init

        :param address: miner's address
        :type address: str
        :param difficulty: difficulty of task estimated by this miner
        :type difficulty: float
        :param result_hash: hash of this miner's result
        :type result_hash: int
        """
        self.difficulty = difficulty
        self.result_hash = result_hash
        self.address = address

    def run(self, task):
        """
        Run task

        :param task: task to run
        """
        t = task
        t.run()
        self.difficulty = t.difficulty
        self.result_hash = t.result_hash()
        return t.result_dump()

    def __hash__(self):
        """
        Needed to index miners

        :return: hash of miner's address
        :rtype: str
        """
        return mmh3.hash(self.address)

    def __str__(self):
        """
        String representation of TaskMiner

        :return: representation
        :rtype: str
        """
        return json.dumps((self.address, self.difficulty, self.result_hash))

    @classmethod
    def from_json(cls, s):
        """
        Restore TaskMiner from JSON

        :param s: representation
        :rtype s: str
        :return: TaskMiner
        :rtype: TaskMiner
        """
        return cls(*json.loads(s))


class Task:
    def __init__(self, parent, n, task_class, miners=tuple(), task_data=None):
        """
        init

        :param parent: sc-parent index
        :type parent: list
        :param n: number of this task in sc
        :type n: int
        :param task_class: executor type (str, 'js' or 'wasm')
        :type task_class: str
        :param miners
        :type miners: list
        :param task_data: task data
        :type task_data: str
        """
        self.parent = parent
        self.n = n
        self.miners = list(miners)
        self.task_class = task_class
        self.done = False
        if task_data:
            if task_class == 'js':
                self.task = js[0].from_json(task_data)
        else:
            self.task = None

    def awards(self):
        """
        Calculate awards

        :return: awards
        :rtype: dict
        """
        results = dict(Counter([miner.result_hash for miner in self.miners]))
        results, numbers = results.keys(), results.values()
        number = max(numbers)
        if list(numbers).count(number) > 1:
            return {}
        result = list(results)[list(numbers).index(number)]
        awards = {}
        for miner in self.miners:
            if miner.result_hash == result:
                awards[miner.address] = miner.difficulty
        self.done = True
        return awards

    def find_miner(self, address):
        """
        Find miner by address

        :param address: miner's address
        :type address: str
        :return: miner
        :rtype: TaskMiner
        """
        for m in self.miners:
            if m.address == address:
                return m

    def set_miner(self, address, miner):
        """
        Update miner by address (if task is solved)

        :param address: address of miner
        :type address: str
        :param miner: TaskMiner object
        :type miner: TaskMiner
        """
        for i, m in enumerate(self.miners):
            if m.address == address:
                self.miners[i] = miner
                return

    def task_application(self, miner):
        """
        Add miner to task

        :param miner: miner to add
        :return:
        """
        if len(self.miners) >= MAXMINERS:
            return False
        if hash(miner) in map(hash, self.miners):
            return False
        self.miners.append(miner)
        return True

    def is_open(self):
        """
        If task is open: are new miners needed

        :return: is task open or not
        :rtype: bool
        """
        return len(self.miners) <= MAXMINERS and not self.done

    def __hash__(self):
        """
        Hash of task

        :return: hash
        :rtype: int
        """
        return mmh3.hash(json.dumps((self.parent, self.n)))

    def __str__(self):
        """
        Convert task to JSON

        :return: task's JSON representation
        :rtype: str
        """
        return json.dumps((self.parent, self.n, [str(miner) for miner in self.miners], self.task_class, str(self.task)))

    @classmethod
    def from_json(cls, s):
        """
        Restore task from JSON

        :param s: task's JSON representation (from Task.__str__)
        :type s: str
        :return: task
        :rtype: Task
        """
        s = json.loads(s)
        miners = [TaskMiner.from_json(st) for st in s[2]]
        return cls(s[0], s[1], s[3], miners, s[4])

import json
from collections import Counter


class TaskMiner:
    def __init__(self, difficulty=None, result_hash=None, address=None):
        self.difficulty = difficulty
        self.result_hash = result_hash
        self.address = address

    def __str__(self):
        return json.dumps((self.address, self.difficulty, self.result_hash))

    @classmethod
    def from_json(cls, s):
        return cls(*json.loads(s))


class Task:
    def __init__(self, parents, task_class, miners=tuple()):
        """
        init
        :param parents: sc-parent index
        :type parents: list
        :param task_class: executor type (str, 'js' or 'wasm')
        :type task_class: str
        :param miners
        :type miners: list
        """
        self.parent = parents
        self.miners = list(miners)
        self.task_class = task_class

    def awards(self):
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
        return awards

    def __str__(self):
        return json.dumps((self.parent, [str(miner) for miner in self.miners], self.task_class))

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        miners = [TaskMiner.from_json(st) for st in s[1]]
        return cls(s[0], s[2], miners)

import json
import mmh3
import time


class PoWMiner:
    """
    Proof-of-work miner
    pubkey - miner's address
    """
    def __init__(self, pubkey):
        self.pubkey = pubkey
        self.tasks = []

    def to_time(self, fr=0, to=0):
        if to == 0 and fr == 0:
            return self
        if to == 0:
            to = time.time() + 1000
        other = self
        for i in range(len(other.tasks)):
            if not fr < other.tasks[i].time < to:
                other.tasks.pop(i)
        return other

    def __str__(self):
        return json.dumps((self.pubkey, [str(task) for task in self.tasks]))

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        self = cls(s[0])
        self.tasks = s[1]   # todo: write class PoWTask, do PoWTask.from_json
        return self

    def __hash__(self):
        return mmh3.hash(str(self))


class PoKMiner:
    """
    PoK miner
    pubkey - miner's address
    """
    def __init__(self, pubkey):
        self.pubkey = pubkey
        self.tasks = []

    def to_time(self, fr=0, to=0):
        if to == 0 and fr == 0:
            return self
        if to == 0:
            to = time.time() + 1000
        other = self
        for i in range(len(other.tasks)):
            if not fr < other.tasks[i].time < to:
                other.tasks.pop(i)
        return other

    def __str__(self):
        return json.dumps((self.pubkey, [str(task) for task in self.tasks]))

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        self = cls(s[0])
        self.tasks = s[1]  # todo: write class PoKTask, do PoKTask.from_json
        return self

    def __hash__(self):
        return mmh3.hash(str(self))


class Miners:
    """
    This class stores all miners in network after block -1 and some random blocks
    """
    def __init__(self):
        self.pow_miners = []
        self.pok_miners = []

    def hashlist(self, to=0, fr=0):
        return [hash(miner.to_time(to=to, fr=fr)) for miner in self.pow_miners], \
               [hash(miner.to_time(to=to, fr=fr)) for miner in self.pok_miners]

    def __str__(self):
        return json.dumps(([str(miner) for miner in self.pow_miners], [str(miner) for miner in self.pok_miners]))

    @classmethod
    def from_json(cls, s):
        self = cls()
        self.pow_miners, self.pok_miners = json.loads(s)
        self.pow_miners = [PoWMiner.from_json(miner) for miner in self.pow_miners]
        self.pok_miners = [PoKMiner.from_json(miner) for miner in self.pok_miners]
        return self

    def by_time(self, fr=0, to=0):
        """
        miners' tasks in time from {fr} to {to}
        :param fr: from, minimal time
        :param to: to, maximal time
        :return: Miners
        """
        other = self
        for i in range(len(other.pow_miners)):
            other.pow_miners[i] = other.pow_miners[i].to_time(fr=fr, to=to)
        for i in range(len(other.pok_miners)):
            other.pok_miners[i] = other.pok_miners[i].to_time(fr=fr, to=to)
        return other

    def __hash__(self):
        return mmh3.hash(str(self))

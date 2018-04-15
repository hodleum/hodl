import block
import json
bch = block.Blockchain()


with open('tmp/sc.ind', 'r') as f:
    ind = json.loads(f.readlines()[0])

def tnx(outs, outns):
    pass


def append_tasks(task):
    with open('tmp/sc.tasks', 'rw') as f:
        f.write(json.dumps(task) + '\n')


def get_self():
    return bch[list(ind)[0]].contracts[list(ind)[1]]

class TnxIter:
    def __init__(self, bch):
        self.start = True
        self.bc = 0
        self.tc = 0
        self.bch = bch

    def __iter__(self):
        self.current = [self.bc, 0]
        self.tc_curr = self.tc
        self.tc_c = False
        return self

    def __next__(self):
        if not self.tc_c and not self.start:
            self.tc_curr += 1
            if self.tc_curr == len(self.bch[self.bc-1].txs):
                self.tc_c = True
            return self.bch[self.bc-1].txs[self.tc_curr-1]
        else:
            if not (self.current[0]==len(self.bch)-1 and self.current[1] == len(self.bch[self.current[0]].txs)-1):
                if self.current[1] + 1 < len(self.bch[self.current[0]].txs):
                    self.current[1] += 1
                    return self.bch[self.current[0]].txs[self.current[1]-1]
                else:
                    self.current[0] += 1
                    self.current[1] = 1
                    return self.bch[self.current[0]].txs[self.current[1]-1]

    def __str__(self):
        return json.dumps([len(self.bch), len(self.bch[-1].txs)])

    @classmethod
    def from_json(cls, s, bch):
        self = cls(bch)
        l = json.loads(s)
        self.bc, self.tc = l
        self.start = False
        return self

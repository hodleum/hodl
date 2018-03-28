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


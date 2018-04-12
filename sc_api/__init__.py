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
    print('print(list(ind), len(bch), len(bch[0].contracts))', list(ind), len(bch), len(bch[0].__dict__))
    return bch[list(ind)[0]].contracts[list(ind)[1]]


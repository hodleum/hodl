import block
import json
import os


bch = block.Blockchain()
def tnx(outs, outns):
    pass


def append_tasks(task):
    with open('sc.tasks', 'rw') as f:
        f.write(json.dumps(task) + '\n')


def get_self():
    return bch[list(ind)[0]].contracts[list(ind)[1]]


ind = get_self().index

import block
import json
import os


bch = block.Blockchain()
ind = os.listdir()[0].split(']')[0] + ']'
def tnx(outs, outns):
    pass


def append_tasks(task):
    with open('{}.tasks'.format(ind), 'rw') as f:
        f.write(json.dumps(task) + '\n')


def get_self():
    return bch[list(ind)[0]].contracts[list(ind)[1]]

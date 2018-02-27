from sc_api import *
import cryptogr as cg

balances, bc = json.loads(open('sc.mem'.format(ind), 'r').readlines())   # bc - number of last processed block


def add_task(sender, task):
    if sender == get_self().author:
        append_tasks(task)


def write():
    with open('sc.mem', 'w') as f:
        f.write(json.dumps(balances))


def send(sender, money, to):
    if sender in balances.keys():
        if balances[sender] > money and money > 0:
            balances[sender] -= money
            balances[to] += money


def sell(sender, money):
    if sender in balances.keys():
        if balances[sender] >= money:
            balances[sender] -= money
            tnx([sender], [money])


for b in bch[bc:-1]:
    for tnx in b.txs:
        if 'sc' + ind in tnx.outs:
            try:
                balances[tnx.author] += tnx.outns[tnx.outs.index('sc' + ind)]
            except:
                balances[tnx.author] = tnx.outns[tnx.outs.index('sc' + ind)]
write()
with open('sc.mem', 'rw') as f:
    f.write('abc')

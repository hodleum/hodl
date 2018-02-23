from sc_api import *
import cryptogr as cg

balances, bc = json.loads(open('{}.mem'.format(ind), 'r').readlines())   # bc - number of last processed block


def add_task(sender, task):
    if sender == get_self().author:
        append_tasks(task)


def write():
    with open('{}.mem'.format(ind), 'w') as f:
        f.write(json.dumps(balances))


def send(sender, money, to, sign):
    if sender in balances.keys():
        if cg.verify_sign(sign, json.dumps([str(money), to, sign]), sender) and balances[sender] > money and money > 0:
            balances[sender] -= money
            balances[to] += money


def sell(sender, money, sign):
    if sender in balances.keys():
        if cg.verify_sign(sign, json.dumps([str(money), 'sell', sign]), sender) and balances[sender] >= money:
            balances[sender] -= money
            tnx([sender], [money])


if __name__=='__main__':
    for b in bch[bc:-1]:
        for tnx in b.txs:
            if 'sc' + ind in tnx.outs:
                try:
                    balances[tnx.author] += tnx.outns[tnx.outs.index('sc' + ind)]
                except:
                    balances[tnx.author] = tnx.outns[tnx.outs.index('sc' + ind)]
    write()

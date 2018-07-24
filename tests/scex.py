import sc_api as s
import json
import block
import cryptogr as cg


balances, bc, tc = {}, 0, 0
start = True


def add_task(sender, task):
    if sender == s.get_self().author:
        s.append_tasks(task)


def send(sender, money, to):
    if sender in balances.keys():
        if balances[sender] > money and money > 0:
            balances[sender] -= money
            balances[to] += money


def sell(sender, money):
    if sender in balances.keys():
        if balances[sender] >= money:
            balances[sender] -= money
            s.tnx([sender], [money])
            write()


balances['0'] = 0.2
while True:
    if not start:
        if tc != len(s.bch[bc-1].txs):
            for tnx in s.bch[bc-1].txs[tc:len(s.bch[bc-1].txs)]:
                if 'sc' + str(ind) in tnx.outs:
                    try:
                        balances[tnx.author] += tnx.outns[tnx.outs.index('sc' + str(ind))]
                    except:
                        balances[tnx.author] = tnx.outns[tnx.outs.index('sc' + str(ind))]
    if start:
        start = False
    if bc != len(s.bch):
        for i in range(bc, len(s.bch)):
            for tnx in s.bch[i].txs:
                if 'sc' + str(ind) in tnx.outs:
                    try:
                        balances[tnx.author] += tnx.outns[tnx.outs.index('sc' + str(ind))]
                    except:
                        balances[tnx.author] = tnx.outns[tnx.outs.index('sc' + str(ind))]

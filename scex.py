import sc_api as s
import json
import cryptogr as cg

try:
    balances, bc = json.loads(open('tmp/sc.mem', 'r').readline())   # bc - number of last processed block
    bc = int(bc)
except ValueError:
    balances, bc = {}, 0


def add_task(sender, task):
    if sender == s.get_self().author:
        s.append_tasks(task)


def write():
    with open('tmp/sc.mem', 'w') as f:
        bc = len(s.bch)
        f.write(json.dumps((balances, len(s.bch))))


def send(sender, money, to):
    if sender in balances.keys():
        if balances[sender] > money and money > 0:
            balances[sender] -= money
            balances[to] += money


def sell(sender, money):
    print('selling', balances[sender], money, balances[sender]-money)
    print('==============================================================================')
    if sender in balances.keys():
        if balances[sender] >= money:
            balances[sender] -= money
            s.tnx([sender], [money])
            print(balances[sender], '\n')
            write()


for i in range(bc, len(s.bch)):
    print('l', len(s.bch[0].txs))
    for tnx in s.bch[i].txs:
        if 'sc' + str(ind) in tnx.outs:
            try:
                balances[tnx.author] += tnx.outns[tnx.outs.index('sc' + str(ind))]
            except:
                balances[tnx.author] = tnx.outns[tnx.outs.index('sc' + str(ind))]
balances['0'] = 0.2
write()

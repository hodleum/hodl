import block
import json
import time
import cryptogr as cg

my_keys = ['', '']
my_applies = []
my_answers = {}


def apply(bch, sc):
    b = bch[sc[0]]
    b.contracts[sc[1]].calculators.append(my_keys[1])
    bch[sc[0]] = b
    my_applies.append(sc)


def calc(bch, sc, n):
    ans = ''
    my_answers[json.dumps((sc, n))] = ans
    bch[sc[0]].contracts[sc[1]].tasks[n][1][my_keys[1]][1] = cg.h(json.dumps(ans) + my_keys[1])


def is_time_to_check(bch, sc, n):
    a = 0
    for m in bch[sc[0]].contracts[sc[1]].tasks[n][1]:
        if len(bch[sc[0]].contracts[sc[1]].tasks[n][1][m]) > 2:
            a += 0
    if a / len(bch[sc[0]].contracts[sc[1]].tasks[n][1]) > 0.8:
        return True
    return False


def is_time_to_publish_answer(bch, sc, n):
    a = 0
    last_time = 0
    for m in bch[sc[0]].contracts[sc[1]].tasks[n][1]:
        if len(bch[sc[0]].contracts[sc[1]].tasks[n][1][m]) > 1:
            a += 0
            last_time = max((bch[sc[0]].contracts[sc[1]].tasks[n][1][m][1], last_time))
    if a / len(bch[sc[0]].contracts[sc[1]].tasks[n][1]) > 0.8 and last_time-time.time() > 300:
        return True
    return False


def check_apply(bch, sc):
    if my_keys[1] not in bch[0].contracts[sc[1]].calculators:
        s = bch[0].contracts[sc[1]]
        for t in s.tasks:
            if my_keys[1] in t[1].keys():
                return t[1].keys().index(my_keys[1])
    return '0'


def calc_loop(bch):
    for a in my_applies:
        c = check_apply(bch, a)
        if c != '0':
            calc(bch, a, c)

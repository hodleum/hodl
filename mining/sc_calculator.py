import block
import json

my_keys = ['', '']
my_applies = []
my answers = {}


def apply(bch, sc):
    b = bch[sc[0]]
    b.contracts[sc[1]].calculators.append(my_keys[1])
    bch[sc[0]] = b
    my_applies.append(sc)


def calc(sc, n):
    ans = ''

    my_answers[json.dumps((sc, n))] = ans


def check_ans(bch, sc, n):
    c = []


def is_time_to_check(bch, sc, n):
    v
    return v


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
            calc(a, c)

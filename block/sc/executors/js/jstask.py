import json
import time
from threading import Thread
from cryptogr import h
from block.sc.executors.js.jstools import CTX


BENCHMARK = None


def benchmark():
    ctx = CTX()
    ts = time.time()
    ctx.run_script('for (var i =0;i<200000000;i++){Math.pow(5,1000)}')
    BENCHMARK = time.time() - ts


Thread(target=benchmark).start()


class JSTask:
    def __init__(self, code):
        self.code = code
        # todo: execution time/benchmark time
        self.done = False
        self.ans = None
        self.difficulty = 1
        self.context = None

    def run(self, ctx):
        ctx = CTX.from_json(ctx)
        while not BENCHMARK:
            time.sleep(0.1)
        t1 = time.time()
        ctx.run_script(self.code)
        self.difficulty = (time.time() - t1) / BENCHMARK
        self.ans = ctx.run_script('__answer__')
        ctx.run_script('__answer__=""')
        self.context = str(ctx)
        self.done = True

    def __str__(self):
        return json.dumps([self.code, self.done, self.ans, self.difficulty, self.context])

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        self = cls(s[0])
        self.done = s[1]
        self.ans = s[2]
        self.difficulty = s[3]
        self.context = s[4]

    def result_hash(self):
        return h(json.dumps([str(self.context), str(self.ans)]))


def code_to_tasks(code):
    tasks = []
    code = code.split('\n')
    l = 0
    for i in range(len(code)+1):
        if i - l >= 10:
            if code[:i].count('{') == code[:i].count('}'):
                tasks.append(JSTask('\n'.join(code[l:i])))
                l = i
    if l != len(code):
        tasks.append(JSTask('\n'.join(code[l:])))
    return tasks


def msg_task(author, msg):
    return JSTask('''__msg__("{}")'''.format(json.dumps([author, msg])))


def net_task(author, msg):
    return JSTask('''__net__("{}")'''.format(json.dumps([author, msg])))


js = [JSTask, code_to_tasks, msg_task, net_task]

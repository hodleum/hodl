from hodl.cryptogr import h
from hodl.block.sc.executors.js.jstools import CTX
import json
import time
from threading import Thread
import logging as log


BENCHMARK = None


def benchmark():
    ctx = CTX()
    ts = time.time()
    ctx.run_script('for (var i =0;i<200000000;i++){Math.pow(5,1000)}')
    global BENCHMARK
    BENCHMARK = time.time() - ts


Thread(target=benchmark).start()


class JSTask:
    """
    JS Task - a part of JavaScript code with context
    """
    def __init__(self, code):
        self.code = code
        self.done = False
        self.ans = None
        self.difficulty = 1
        self.context = str(CTX())

    def run(self, ctx=None):
        """
        Run JavaScript task
        :param ctx: custom context
        """
        if not ctx:
            ctx = CTX.from_json(self.context)
        if not BENCHMARK:
            print('benchmark not finished')
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
        return self

    def result_hash(self):
        return h(json.dumps([str(self.context), str(self.ans)]))

    def result_dump(self):
        return json.dumps([str(self.context), str(self.ans)])


def split_code_to_tasks(code):
    """
    Splits JS code (str) to tasks
    :param str code: JS code
    :return: list
    """
    tasks = []
    code = code.split('\n')
    last_tasks_last_line = 0
    for i in range(len(code) + 1):
        if i - last_tasks_last_line >= 10:
            code_before = '\n'.join(code[:i])
            if code_before.count('{') == code_before.count('}'):
                tasks.append(JSTask('\n'.join(code[last_tasks_last_line:i])))
                last_tasks_last_line = i
    if last_tasks_last_line != len(code):
        tasks.append(JSTask('\n'.join(code[last_tasks_last_line:])))
    return tasks


def msg_task(author, msg):
    """
    Create task by message to smart contract
    :param str author: message's author
    :param str msg: message
    :return: Task
    :rtype: JSTask
    """
    return JSTask('''__msg__("{}")'''.format(json.dumps([author, msg])))


def net_task(author, msg):
    """
    Create task by HDI request to smart contract
    :param str author: request's author
    :param str msg: request
    :return: Task
    :rtype: JSTask
    """
    return JSTask('''__net__("{}")'''.format(json.dumps([author, msg])))


js = [JSTask, split_code_to_tasks, msg_task, net_task]

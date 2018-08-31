import json
from block.sc.executors.jstools import context, context_to_str, context_from_json


class JSTask:
    def __init__(self, code):
        self.code = code
        # todo: execution time/benchmark time
        self.done = False
        self.ans = None
        self.difficulty = None
        self.context = None

    def run(self, ctx):
        ctx = context_from_json(ctx)
        ctx.run_script(self.code)
        self.ans = ctx.run_script('__answer__')
        ctx.run_script('__answer__=""')
        self.context = context_to_str(ctx)
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


js = [code_to_tasks, msg_task, net_task]

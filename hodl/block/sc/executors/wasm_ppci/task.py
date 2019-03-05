import json

from block.sc.executors.wasm_ppci import rainywasm


class WASMTask:
    def __init__(self, code):
        self.code = code
        # todo
        self.done = False
        self.ans = None
        self.difficulty = None
        self.context = None

    def run(self, ctx):
        # todo
        ctx = rainywasm.WasmProcess.from_json(ctx)
        ctx.run_script(self.code)
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


def code_to_tasks(code):
    tasks = []
    # todo
    return tasks


def msg_task(author, msg):
    return WASMTask('''__msg__("{}")'''.format(json.dumps([author, msg])))


def net_task(author, msg):
    return WASMTask('''__net__("{}")'''.format(json.dumps([author, msg])))


js = [code_to_tasks, msg_task, net_task]

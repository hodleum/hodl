from block.sc.jstools import context, context_to_str, context_from_json


class JSTask:
    def __init__(self, code, ctx):
        self.code = code
        self.context = ctx
        # todo: execution time/benchmark time
        self.done = False

    def run(self):
        ctx = context_from_json(self.context)
        ctx.run_script(self.code)
        self.context = context_to_str(ctx)
        self.done = True

    def fill_ctx(self, prevtask):
        self.context = prevtask.context


def code_to_tasks(code):
    tasks = []
    code = code.split('\n')
    l = 0
    for i in range(len(code)):
        if i - l > 10:
            if code[:i].count('{') == code[:i].count('}'):
                tasks.append(JSTask(code[l:i], ''))
                l = i
    return tasks

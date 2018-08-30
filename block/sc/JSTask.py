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


def code_to_tasks(code):
    return [JSTask(code, context_to_str(context()))]

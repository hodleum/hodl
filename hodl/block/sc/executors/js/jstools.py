from v8cffi import shortcuts
import json


shortcuts.set_up()


def bch_replace(ctx, line, bch):
    l = line.split('__bch__[')[1:]
    for i in range(len(l)):
        l[i] = l[i].split(']')[0]
        l[i] = ctx.run_script(l[i])
    line = line.split('__bch__[')
    for i in range(1, len(line)):
        line[i] = '"' + str(bch[int(l[i])]) + '"' + ']'.join(line[i].split(']')[1:])
    '__bch__['.join(line)
    return line


class CTX:
    def __init__(self):
        self.ctx = shortcuts.get_context()
        self.ctx.run_script("var __answer__='';function log(s){__answer__+=s}")

    def __str__(self):
        return json.dumps((self.ctx.run_script('JSON.stringify(this)'), self.ctx.run_script('''var funcs = [];
                                        for (var __obj__ in this){
                                        if (JSON.stringify(this[__obj__])==undefined){funcs.push(String(this[__obj__]))}
                                        }
                                        JSON.stringify(funcs)''')))

    @classmethod
    def from_json(cls, s):
        if not s:
            return cls()
        sess = json.loads(s)
        self = cls()
        self.ctx.run_script("""
                        __session__ = JSON.parse('""" + sess[0] + """')
                        for (var __obj__ in __session__){this[__obj__]=__session__[__obj__]}
                        __functions__ = JSON.parse('""" + sess[1] + """')
                        for (var i=0;i<__functions__.length;i++){eval(__functions__[i])}
                        """)
        return self

    def run_script(self, s, bch=tuple()):
        if '__bch__[' not in s:
            return self.ctx.run_script(s)
        else:
            code = s.split('\n')
            a = 'undefined'
            l = 0
            for i in range(len(code)):
                if '__bch__[' in code[i]:
                    a = self.ctx.run_script('\n'.join(code[l:i]))
                    l = i + 1
                    a = self.ctx.run_script(bch_replace(self.ctx, code[i], bch))
            return a

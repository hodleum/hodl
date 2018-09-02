from v8cffi import shortcuts
import json


shortcuts.set_up()


class CTX:
    def __init__(self):
        self.ctx = shortcuts.get_context()
        self.ctx.tear_down()
        self.ctx.set_up()
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

    def run_script(self, s):
        return self.ctx.run_script(s)

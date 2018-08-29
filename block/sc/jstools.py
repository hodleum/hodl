from v8cffi import shortcuts
import json


shortcuts.set_up()


def context():
    ctx = shortcuts.get_context()
    ctx.tear_down()
    ctx.set_up()
    return ctx


def context_to_str(ctx):
    return json.dumps((ctx.run_script('JSON.stringify(this)'), ctx.run_script('''var funcs = [];
                                    for (var __obj__ in this){
                                    if (JSON.stringify(this[__obj__])==undefined){funcs.push(String(this[__obj__]))}
                                    }
                                    JSON.stringify(funcs)''')))


def context_from_json(s):
    sess = json.loads(s)
    ctx = context()
    ctx.run_script("""
                    __session__ = JSON.parse('""" + sess[0] + """')
                    for (var __obj__ in __session__){this[__obj__]=__session__[__obj__]}
                    __functions__ = JSON.parse('""" + sess[1] + """')
                    for (var i=0;i<__functions__.length;i++){eval(__functions__[i])}
                    """)
    return ctx

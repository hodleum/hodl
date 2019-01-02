import block
from block.sc.executors.js.jstask import JSTask
from block.sc.executors.js.jstools import CTX
from block.sc import SmartContract
import unittest
import cryptogr as cg
import json
import os

my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]


class TestSmartContracts(unittest.TestCase):
    def test_creation(self):
        sc = SmartContract('__answer__="hello, world"', my_keys[1], [1, 1])
        sc.sign_sc(my_keys[0])

    def test_str(self):
        sc = SmartContract('__answer__="hello, world"', my_keys[1], [1, 1])
        self.assertEqual(str(SmartContract.from_json(str(sc))), str(sc))


class TestTaskExecutors(unittest.TestCase):
    def test_js(self):
        task = JSTask('__answer__="hello, world!"')
        task.run()
        self.assertEqual(task.ans, "hello, world!")

    def test_ctx_str(self):
        ctx = CTX()
        ctx.run_script('''a="hello"
        function f(x){b=6}
        function g(x){return 23}
        f(6)''')
        self.assertEqual(CTX.from_json(str(ctx)).run_script('b'), '6')
        self.assertEqual(CTX.from_json(str(ctx)).run_script('f'), 'function f(x){b=6}')
        self.assertEqual(CTX.from_json(str(ctx)).run_script('g(5)'), '23')

    def test_task_str(self):
        task = JSTask('''a="hello"
        function f(x){b=6}
        f(6)''')
        task.done = True
        task.ans = '5'
        task.difficulty = 2.0
        task2 = JSTask.from_json(str(task))
        self.assertEqual(task2.done, task.done)
        self.assertEqual(task2.ans, task.ans)
        self.assertEqual(task2.difficulty, task.difficulty)
        self.assertEqual(str(task2), str(task))


if __name__ == '__main__':
    unittest.main()

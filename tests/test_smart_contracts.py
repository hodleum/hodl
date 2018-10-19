import block
from block.sc.executors.js.jstask import JSTask
from block.sc.executors.js.jstools import CTX
import unittest
import cryptogr as cg
import json
import os


my_keys = cg.gen_keys()
your_pub_key = cg.gen_keys()[1]


class TestSmartContracts(unittest.TestCase):
    pass   # todo


class TestTaskExecutors(unittest.TestCase):
    def test_js(self):
        task = JSTask('__answer__="hello, world!"')
        task.run()
        self.assertEqual(task.ans, "hello, world!")
        print('context:\n\n\n', task.context)


if __name__ == '__main__':
    unittest.main()

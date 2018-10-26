import block
import cryptogr as cg
from block.sc.task import TaskMiner, Task
import json
import time


class PoWMiner:
    def __init__(self, address):
        self.address = address
        self.tasks = []
        self.answers = {}

    def task_application_loop(self, bch):
        for tnx in bch.tnxiter():
            if tnx.sc:
                for task in tnx.sc.tasks:
                    if task.is_open():
                        task.task_application(TaskMiner(address=self.address))
                        self.tasks.append(task)

    def run_tasks(self, bch):
        for i in range(len(self.tasks)):
            if self.tasks[i].find_miner(self.address).result_hash:
                self.tasks[i] = self.run_task(self.tasks[i])

    def run_task(self, task):
        """
        Run task
        :param task: task to run
        :return: done task
        """
        my_task = task.find_miner(self.address)
        self.answers[cg.h(str(task.parent))] = my_task.run(task.task)
        task.set_miner(self.address, my_task)
        return task

    def __str__(self):
        return json.dumps([self.address, [str(task) for task in self.tasks], self.answers])

    @classmethod
    def from_json(cls, s):
        s = json.loads(s)
        self = cls(s[0])
        self.answers = s[2]
        self.tasks = [Task.from_json(task) for task in s[1]]
        return self

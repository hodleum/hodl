import block
from block.sc.task import TaskMiner, Task
import cryptogr as cg
import json
import time
import logging as log


# todo: PoW miner which wants to run task gets memory from PoK miner and pushes it after running task


class PoWMiner:
    def __init__(self, address):
        log.info('PoWMiner sc_calculator created')
        self.address = address
        self.tasks = []
        self.answers = {}

    def task_application_loop(self, bch):
        log.info('PoWMiner.task_application_loop')
        for i in range(len(bch)):
            for task in bch[i].sc_tasks:
                if task.is_open():
                    log.info('PoWMiner.task_application_loop: attending task')
                    task.task_application(TaskMiner(address=self.address))
                    self.tasks.append(task)
                    log.info('PoWMiner.task_application_loop: attended task')

    def run_tasks(self, bch):
        log.info(f'PoWMiner.run_tasks. len(self.tasks): {len(self.tasks)}')
        for i in range(len(self.tasks)):
            if not self.tasks[i].find_miner(self.address).result_hash:
                log.info('PoWMiner.run_tasks: found task')
                try:
                    index = [hash(task) for task in bch[-1].sc_tasks].index(hash(self.tasks[i]))
                except ValueError:
                    log.info(f'task with hash {hash(self.tasks[i])} is outdated')
                    continue
                self.tasks[i] = self.run_task(self.tasks[i])
                log.info('PoWMiner.run_tasks:task done')
                b = bch[-1]
                b.sc_tasks[index] = self.tasks[i]
                bch[-1] = b
        log.info('PoWMiner.run_tasks done')

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

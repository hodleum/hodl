from hodl.block.sc.task import TaskMiner, Task
from hodl import cryptogr as cg
import json
import time
import logging as log
from multiprocessing import Process


# todo: PoW miner which wants to run task gets memory from PoK miner and pushes it after running task


class PoWMiner:
    def __init__(self, address, privkey):
        log.info('PoWMiner sc_calculator created')
        self.address = address
        self.privkey = privkey
        self.tasks = []
        self.answers = {}

    def task_application(self, bch):
        for i in range(len(bch)):
            b = bch[i]
            for j in range(len(b.sc_tasks)):
                if b.sc_tasks[j].is_open() and b.sc_tasks[j] not in self.tasks:
                    if b.sc_tasks[j].task_application(TaskMiner(address=self.address)):
                        self.tasks.append(b.sc_tasks[j])
                        log.info(f"PoWMiner.task_application_loop: attended task of SC {b.sc_tasks[j].parent}. len of "
                                 f"its' miners list: {len(b.sc_tasks[j].miners)}")
                        bch[i] = b

    def run_task(self, task):
        """
        Run task

        :param task: task to run
        :return: done task
        """
        my_task = task.find_miner(self.address)
        self.answers[cg.h(str(task.parent))] = my_task.run(task.task)
        task.set_miner(self.address, my_task)
        # todo: send info to PoK miner
        return task

    def run_tasks(self, bch):
        """
        Run all available tasks

        :param bch: blockchain
        :type bch: Blockchain
        """
        if len(self.tasks):
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

    def main_process(self, bch):
        """
        Start mining loop in another process

        :param bch: blockchain
        :type bch: Blockchain
        """
        def task_application_loop():
            while True:
                self.task_application(bch)
                time.sleep(1)

        def task_running_loop():
            while True:
                self.run_tasks(bch)
        Process(target=task_application_loop, name='PoW task application loop').start()
        Process(target=task_running_loop, name='PoW task running loop').start()

    def __str__(self):
        """
        Get string representation of PoW miner

        :return: representation
        :rtype: str
        """
        return json.dumps([self.address, [str(task) for task in self.tasks], self.answers])

    @classmethod
    def from_json(cls, s):
        """
        Restore PoW miner from JSON

        :param s: string representation
        :type s: str
        :return: PoWMiner
        """
        s = json.loads(s)
        self = cls(s[0])
        self.answers = s[2]
        self.tasks = [Task.from_json(task) for task in s[1]]
        return self

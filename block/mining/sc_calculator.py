import block
import json
import time
import cryptogr as cg


class PoWMiner:
    def __init__(self, address):
        self.address = address
        self.applies = []
        self.answers = {}

    def task_application(self, index, bch):
        pass   # todo

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

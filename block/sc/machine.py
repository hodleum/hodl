"""
VPy config
"""
import vpy


class DFS:
    """
    Decentralized FileSystem - class for storing filesystem and global vars for VPy
    """
    def __getitem__(self, item):
        pass   # todo

    def __setitem__(self, key, value):
        pass   # todo

    def __delitem__(self, key):
        pass   # todo


class Proc:
    """
    class for VPy's calculations
    """
    def __init__(self):
        self.tasks = []
        self.done_tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        # todo

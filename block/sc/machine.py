"""
VPy config
"""
from vpy.fs import FS
from vpy.proc import Proc


class DFS(FS):
    """
    Decentralized FileSystem - class for storing filesystem and global vars for VPy
    """
    def __getitem__(self, item):
        pass   # todo

    def __setitem__(self, key, value):
        pass   # todo

    def __delitem__(self, key):
        pass   # todo

    def __len__(self):
        pass   # todo

    def add(self, data):
        pass   # todo


class DProc(Proc):
    """
    class for VPy's calculations
    """
    def __init__(self):
        self.tasks = []
        self.done_tasks = []

    def add_task(self, task):
        self.tasks.append(task)
        # todo

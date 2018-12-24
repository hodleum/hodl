"""
VPy config
"""
from vpy.proc import Proc


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
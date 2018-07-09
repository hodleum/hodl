import time


class TempDict(dict):

    update = 5

    def __init__(self, *args):
        self.last_check = time.time()
        super().__init__(*args)

    def __setitem__(self, key, value, expire=20):
        self.check()
        super().__setitem__(key, {
            'time': time.time(),
            'expire': expire,
            'value': value
        })

    def __getitem__(self, item):
        self.check()
        return super().__getitem__(item)['value']

    def check(self):
        if time.time() - self.last_check < self.update:
            return
        for key, value in self.copy().items():
            if time.time() - value['time'] >= value['expire']:
                del self[key]

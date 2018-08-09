import dpath.util


class DFS:
    """
    Decentralized filesystem
    Necessary functions:
    __setitem__
    __delitem__
    append
    __len__
    """
    def __init__(self):
        self.sys = {}

    def read_file(self, path):
        f = dpath.util.get(self.sys, path)
        return self[f[0]:f[1]]
    
    def write_file(self, path, data):
        path = path.split('/')
        f = self.sys
        for name in path[:-1]:
            f = f[name]
        if path[-1] in f.keys():
            del self[f[0]:f[1]]
            self[f[0]:f[0]] = data
            self._shift(f[0], len(data))
        else:
            dpath.util.new(self.sys, path, [len(self), len(self) + len(data)])
            self.plus(data)

    def _shift(self, level, shift):
        # iterate for each file and shift number if number > level
        pass    # todo

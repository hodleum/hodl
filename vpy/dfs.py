import dpath.util


def shift(d, level, length):
    for key in d.keys():
        if type(d[key]) == dict:
            d[key] = shift(d[key], level, length)
        else:
            if d[key][0] > level:
                d[key][0] += length
            if d[key][1] > level:
                d[key][1] += length
    return d


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

    def new_folder(self, path):
        dpath.util.new(self.sys, path, {})

    def _shift(self, level, length):
        self.sys = shift(self.sys, level, length)

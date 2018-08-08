class DFS:
    def __init__(self):
        self.sys = {}

    def read_file(self, path):
        path = path.split('/')
        f = self.sys
        for name in path:
            f = f[name]
        return self[f[0]:f[1]]
    
    def write_file(self, path, data):
        path = path.split('/')
        f = self.sys
        for name in path:
            f = f[name]
        self[f[0]:f[1]] = data

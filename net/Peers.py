import json


class Peers(set):
    """
    Class for storing peers.
    """
    def save(self, file):
        with open(file, 'w') as f:
            f.write(json.dumps([json.dumps(peer) for peer in list(self)]))

    def open(self, file):
        with open(file, 'r') as f:
            for peer in json.loads(f.read()):
                self.add(json.loads(peer))

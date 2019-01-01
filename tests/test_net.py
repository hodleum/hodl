import unittest
from subprocess import Popen
from sys import stdout, stderr
import time
from threading import Thread
import json

from hodl.net2.protocol import server as main_server, protocol
from hodl.net2.models import Peer, Message, create_db, drop_db


class NetTest(unittest.TestCase):
    server_counts = 10
    servers = []

    @classmethod
    def setUpClass(cls):

        time.sleep(1)
        for i in range(8001, 8000 + cls.server_counts):
            cls.change_config(i)
            cls.servers.append(Popen(['python', 'net_starter.py', str(i)], stdout=stdout, stderr=stderr))
            time.sleep(1)
        time.sleep(3)

    def test_share_peers(self):
        for i in range(8001, 8000 + self.server_counts):
            peer = Peer(protocol, addr=f'127.0.0.1:{i}')
            peer.request(Message('ping'))
        time.sleep(3)
        self.assertAlmostEqual(len(protocol.peers), self.server_counts, delta=1)
        protocol.send_all(Message('ping'))
        time.sleep(1)

    @staticmethod
    def change_config(port):
        with open('net2/config.json') as inp:
            configs = json.load(inp)
            configs['port'] = port
            configs['name'] = str(port)
            with open('net2/config.json', 'w') as out:
                json.dump(configs, out, indent=2)

    @classmethod
    def tearDownClass(cls):
        for server in cls.servers:
            server.kill()

        cls.change_config(8000)


if __name__ == '__main__':
    test_thread = Thread(target=unittest.main)
    drop_db()
    create_db()
    main_server.reactor.callLater(0, test_thread.start)

    main_server.run(8000)

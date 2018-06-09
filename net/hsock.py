from socket import socket
import multiprocessing
import time
from net.Peers import Peers
import cryptogr


class HSock:
    """
    HODL socket:
    Helps to connect any device connected to HODL network (including devices behind NAT)
    """
    def __init__(self, sock=None, conn=None, addr='', myaddrs=[], peers=Peers()):
        if not (sock and conn):
            peer = peers.srchbyaddr(addr)
            if peer.is_white(myaddrs):
                # create self.sock, self.conn
                # todo
                pass
            else:
                # todo
                # create connection (self.conn) between this device and white peer, which connects to this peer.
                # Generate RSA keys.
                pass
        else:
            self.sock = sock
            self.conn = conn
        self.in_msgs = []
        # start listen as daemon (using multiprocessing) and put messages to self.in_msgs
        self.l = multiprocessing.Process(target=self.listen)
        self.l.start()
        self.l.join()

    @classmethod
    def input(cls, sock, conn):
        self = cls(sock=sock, conn=conn)

    def send(self, data):
        # todo: encode data using RSA
        self.conn.send(data.encode())

    def listen(self):
        """
        Listen for new messages and write it to self.in_msgs
        :return:
        """
        data = b''
        while True:
            p = self.conn.recv(1024)
            if not p:
                self.in_msgs.append(data.decode())
                data = b''
            data += p

    def close(self):
        """
        Close socket.
        :return:
        """
        self.conn.close()
        self.l.terminate()

    def listen_msg(self, delt=0.05):
        l = len(self.in_msgs)
        while True:
            time.sleep(delt)
            if len(self.in_msgs) > l:
                return self.in_msgs[-1]


def listen():
    sock = socket()
    sock.bind(('', 5000))
    sock.listen(1)
    conn, addr = sock.accept()
    return HSock.input(sock, conn)

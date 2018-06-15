from socket import socket
from threading import Thread
import time
from net.Peers import Peers
import cryptogr
import struct


def recv(conn):
    chunk = conn.recv(4)
    if len(chunk) < 4:
        return
    slen = struct.unpack('>L', chunk)[0]
    chunk = conn.recv(slen)
    while len(chunk) < slen:
        chunk += conn.recv(slen - len(chunk))
    return chunk


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
            self.socks = [sock]
            self.conns = [conn]
        self.in_msgs = []
        # start listen as daemon (using multiprocessing) and put messages to self.in_msgs
        self.l = Thread(target=self.listen)
        self.l.start()

    @classmethod
    def input(cls, sock, conn):
        self = cls(sock=sock, conn=conn)

    def send(self, data):
        # todo: encode data using RSA
        data = struct.pack('>L', len(data)) + data
        for conn in self.conns:
            conn.send(data.encode())

    def listen(self):
        """
        Listen for new messages and write it to self.in_msgs
        :return:
        """
        # todo: decode msg using RSA
        for conn in self.conns:
            Thread(target=self.recv_by_conn, args=(conn, )).start()

    def close(self):
        """
        Close socket.
        :return:
        """
        for conn in self.conns:
            conn.close()

    def recv_by_conn(self, conn):
        while True:
            self.in_msgs.append(recv(conn))

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

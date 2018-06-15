from socket import socket
from threading import Thread
import time
from net.Peers import Peers
import cryptogr
import struct


def recv(sock):
    chunk = sock.recv(4)
    if len(chunk) < 4:
        return
    slen = struct.unpack('>L', chunk)[0]
    chunk = sock.recv(slen)
    while len(chunk) < slen:
        chunk += sock.recv(slen - len(chunk))
    return chunk


class HSock:
    """
    HODL socket:
    Helps to connect any device connected to HODL network (including devices behind NAT)
    """
    def __init__(self, sock=None, conn=None, addr='', myaddrs=[], peers=Peers(), log=None):
        if not (sock and conn):
            if log:
                log.debug('HSock.__init__: creating HSock by connecting by address')
            peer = peers.srchbyaddr(addr)
            self.socks = peer.connect(peers, log=log)
        else:
            if log:
                log.debug('HSock.__init__: creating input HSock by conn and sock')
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
        for sock in self.socks:
            sock.send(data.encode())

    def listen(self):
        """
        Listen for new messages and write it to self.in_msgs
        :return:
        """
        # todo: decode msg using RSA
        for sock in self.socks:
            Thread(target=self.recv_by_sock, args=(sock, )).start()

    def close(self):
        """
        Close socket.
        :return:
        """
        for conn in self.conns:
            conn.close()

    def recv_by_sock(self, sock):
        while True:
            self.in_msgs.append(recv(sock))

    def listen_msg(self, delt=0.05):
        l = len(self.in_msgs)
        while True:
            time.sleep(delt)
            if len(self.in_msgs) > l:
                return self.in_msgs[-1]


class BetweenSock:
    def __init__(self, conn, sock):
        self.inconn = conn
        self.insock = sock
        # get addr using sock
        self.outsock = socket()
        # create self.outconn
        # todo


def listen():
    sock = socket()
    sock.bind(('', 5000))
    sock.listen(1)
    conn, addr = sock.accept()
    return HSock.input(sock, conn)

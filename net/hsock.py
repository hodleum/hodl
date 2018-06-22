from socket import socket
from threading import Thread
import time
from net.Peers import Peers
import logging as log
from .proto import recv, send
import json5 as json

class HSock(Thread):
    """
    HODL Socket:
    Helps to connect any device connected to HODL network (including devices behind NAT)
    """
    def __init__(self, sock=None, conn=None, addr='', myaddrs=(), peers=Peers()):
        if not (sock and conn):
            log.debug('HSock.__init__: creating HSock by connecting by address')
            peer = peers.srchbyaddr(addr)[1]
            self.socks = peer.connect(peers)
        else:
            log.debug('HSock.__init__: creating input HSock by conn and sock')
            self.socks = [sock]
            self.conns = [conn]
        self.in_msgs = []

        super().__init__(self.listen())
        self.name = addr
        self.start()

    @classmethod
    def input(cls, sock, conn):
        log.debug('hsock.HSock.input from sock and conn: ' + str(sock) + ', ' + str(conn))
        return cls(sock=sock, conn=conn)

    def send(self, data):
        # todo: encode data using RSA
        for sock in self.socks:
            send(sock, data.encode('utf-8'))

    def listen(self):
        """
        Listen for new messages and write it to self.in_msgs
        :return:
        """
        # todo: decode msg using RSA
        for sock in self.socks:
            if sock:
                Thread(target=self.recv_by_sock, args=(sock, )).start()

    def close(self):
        """
        Close socket.
        :return:
        """
        for conn in self.conns:
            conn.close()

    def recv_by_sock(self, sock):

        self.in_msgs.append(recv(sock))

    def listen_msg(self, delt=0.05):
        """
        Listen for one msg
        :param delt: float
        :return: msg: str
        """
        len_msg = len(self.in_msgs)
        while True:
            time.sleep(delt)
            if len(self.in_msgs) > len_msg:
                return self.in_msgs[-1]


class BetweenSock:
    def __init__(self, conn, sock):
        self.inconn = conn
        self.insock = sock
        # get addr using sock
        self.outsock = socket()
        # create self.outconn
        # todo


def listen(port=9276):
    """
    Listen for one connection
    :return: sock: HSock
    """
    log.debug('hsock.listen')
    sock = socket()
    sock.bind(('', port))
    sock.listen(1)
    conn, addr = sock.accept()
    log.debug('hsock.listen: input connection')
    return HSock.input(sock, conn)

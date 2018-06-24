from socket import socket
from threading import Thread
import time
from net.Peers import Peers
import logging as log
from .proto import recv, send
import json5 as json


hsocks = []


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
            self.conns = []
        else:
            log.debug('HSock.__init__: creating input HSock by conn and sock')
            self.socks = [sock]
            self.conns = [conn]
        log.debug('HSock.__init__: self.socks, self.conns created. self.socks:' + str([str(sock) for sock in self.socks]))
        self.in_msgs = []
        super().__init__(self.listen())
        self.name = addr
        self.start()
        log.debug('HSock.__init__ self.start finished')

    @classmethod
    def input(cls, sock, conn):
        log.debug('hsock.HSock.input from sock and conn: ' + str(sock) + ', ' + str(conn))
        return cls(sock=sock, conn=conn)

    def send(self, data):
        # todo: encode data using RSA
        for sock in self.socks:
            if sock:
                log.debug('HSock.send: send by sock ' + str(sock))
                send(sock, data.encode('utf-8'))
                log.debug('HSock.send: sent by sock ' + str(sock))

    def listen(self):
        """
        Listen for new messages and write it to self.in_msgs
        :return:
        """
        # todo: decode msg using RSA
        if self.conns:
            for conn in self.conns:
                if conn:
                    Thread(target=self.recv_by_sock, args=(conn,)).start()
        else:
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
        len_msgs = len(self.in_msgs)
        while True:
            time.sleep(delt)
            if len(self.in_msgs) > len_msgs:
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
    hsock = HSock.input(sock, conn)
    hsocks.append(hsock)
    return hsock


def connect_to(addr, myaddrs=tuple(), peers=Peers()):
    for hsock in hsocks:
        if hsock.name == addr:
            return hsock
    else:
        hsock = HSock(addr=addr, myaddrs=myaddrs, peers=peers)


def listen_loop(port=9276):
    while True:
        listen(port)


def listen_thread(port=9276):
    Thread(target=listen_loop, args=(port, )).start()

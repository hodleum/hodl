from socket import socket
import multiprocessing
import time


class HSock:
    """
    HODL socket:
    Helps to connect any device connected to HODL network (including devices behind NAT)
    """
    def __init__(self, addr, myaddrs):
        peer = peers.srchbyaddr(addr)
        if peer.is_white(myaddrs):
            # create self.sock, self.conn
            self.white_peer = True
        else:
            # todo
            # create connection (self.conn) between this device and white peer, which connects to this peer.
            # Generate RSA keys.
            self.white_peer = False
        self.in_msgs = []
        # start listen as daemon (using multiprocessing) and put messages to self.in_msgs
        self.l = multiprocessing.Process(target=self.listen)
        self.l.start()
        self.l.join()

    def send(self, data):
        if self.white_peer:
            self.conn.send(data.encode())
        else:
            # encrypt with RSA and send using self.conn
            pass

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
    data = b''
    while True:
        p = conn.recv(1024)
        data += p
        if not p:
            break

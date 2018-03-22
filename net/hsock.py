from socket import socket
import multiprocessing
import json


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

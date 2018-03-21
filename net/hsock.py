from socket import socket


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

    def send(self, data):
        if self.white_peer:
            self.conn.send(data.encode())
        else:
            # encrypt with RSA and send using self.conn
            pass

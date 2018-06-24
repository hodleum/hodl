from socket import socket
import struct


def sock_to(addr):
    sock = socket()
    sock.connect(addr)
    return sock


def recv(sock):
    """
    Receive function for socket connections

    :type sock: socket
    :return: data (bytes)
    """
    print(sock)
    chunk = sock.recv(4)
    if len(chunk) < 4:
        return
    slen = struct.unpack('>L', chunk)[0]
    print(slen)
    chunk = sock.recv(slen)
    while len(chunk) < slen:
        chunk += sock.recv(slen - len(chunk))
    return chunk


def send(sock, data):
    """
    Send function for socket connections

    :type sock: socket

    :param data: data to send
    :type data: bytes

    :return: None
    """
    if type(data) == str:
        data = data.encode()
    data = struct.pack('>L', len(data)) + data
    sock.sendall(data)

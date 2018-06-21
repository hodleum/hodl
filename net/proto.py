from socket import socket
import struct


def recv(sock):
    """
    Receive function for socket connections

    :type sock: socket
    :return: data (bytes)
    """

    chunk = sock.recv(4)
    if len(chunk) < 4:
        return
    slen = struct.unpack('>L', chunk)[0]
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

    data = struct.pack('>L', len(data)) + data
    sock.sendall(data)
